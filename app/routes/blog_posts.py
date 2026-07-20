from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_admin
from app.core.slugify import slugify
from app.models.blog_post import BlogPost, BlogPostImage, PostStatus
from app.schemas.blog_post import (
    BlogPostCreate,
    BlogPostRead,
    BlogPostSummary,
    BlogPostUpdate,
    GenerateBlogImageRequest,
)
from app.services import cloudinary_service, openai_service

router = APIRouter(prefix="/blog-posts", tags=["blog"])


def _get_post_or_404(post_id: int, session: Session) -> BlogPost:
    post = session.get(BlogPost, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
    return post


def _get_post_image_or_404(post_id: int, image_id: int, session: Session) -> BlogPostImage:
    image = session.get(BlogPostImage, image_id)
    if image is None or image.blog_post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog post image not found"
        )
    return image


def _commit_or_409(session: Session, slug: str) -> None:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A post with slug '{slug}' already exists",
        )


@router.get("", response_model=List[BlogPostSummary])
def list_published_posts(session: Session = Depends(get_session)):
    query = (
        select(BlogPost)
        .where(BlogPost.status == PostStatus.PUBLISHED)
        .order_by(BlogPost.created_at.desc())
    )
    return session.exec(query).all()


@router.get("/slug/{slug}", response_model=BlogPostRead)
def get_published_post_by_slug(slug: str, session: Session = Depends(get_session)):
    post = session.exec(select(BlogPost).where(BlogPost.slug == slug)).first()
    if post is None or post.status != PostStatus.PUBLISHED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
    return post


@router.get(
    "/admin",
    response_model=List[BlogPostSummary],
    dependencies=[Depends(get_current_admin)],
)
def list_all_posts(session: Session = Depends(get_session)):
    return session.exec(select(BlogPost).order_by(BlogPost.created_at.desc())).all()


@router.get(
    "/{post_id}",
    response_model=BlogPostRead,
    dependencies=[Depends(get_current_admin)],
)
def get_post(post_id: int, session: Session = Depends(get_session)):
    return _get_post_or_404(post_id, session)


@router.post(
    "",
    response_model=BlogPostRead,
    dependencies=[Depends(get_current_admin)],
)
def create_post(payload: BlogPostCreate, session: Session = Depends(get_session)):
    slug = slugify(payload.slug or payload.title)
    post = BlogPost(**{**payload.model_dump(exclude={"slug"}), "slug": slug})
    session.add(post)
    _commit_or_409(session, slug)
    session.refresh(post)
    return post


@router.patch(
    "/{post_id}",
    response_model=BlogPostRead,
    dependencies=[Depends(get_current_admin)],
)
def update_post(post_id: int, payload: BlogPostUpdate, session: Session = Depends(get_session)):
    post = _get_post_or_404(post_id, session)

    updates = payload.model_dump(exclude_unset=True)
    if "slug" in updates:
        updates["slug"] = slugify(updates["slug"])

    for field, value in updates.items():
        setattr(post, field, value)

    session.add(post)
    _commit_or_409(session, post.slug)
    session.refresh(post)
    return post


@router.post(
    "/{post_id}/featured-image",
    response_model=BlogPostRead,
    dependencies=[Depends(get_current_admin)],
)
async def upload_featured_image(
    post_id: int,
    file: UploadFile,
    session: Session = Depends(get_session),
):
    post = _get_post_or_404(post_id, session)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be an image"
        )

    image_bytes = await file.read()

    cloudinary_service.delete_image(post.featured_image_public_id)
    secure_url, public_id = cloudinary_service.upload_blog_image(image_bytes)

    post.featured_image_url = secure_url
    post.featured_image_public_id = public_id
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.post(
    "/{post_id}/featured-image/generate",
    response_model=BlogPostRead,
    dependencies=[Depends(get_current_admin)],
)
def generate_featured_image(
    post_id: int,
    payload: GenerateBlogImageRequest,
    session: Session = Depends(get_session),
):
    post = _get_post_or_404(post_id, session)

    image_bytes = openai_service.generate_blog_image(payload.prompt)

    cloudinary_service.delete_image(post.featured_image_public_id)
    secure_url, public_id = cloudinary_service.upload_blog_image(image_bytes)

    post.featured_image_url = secure_url
    post.featured_image_public_id = public_id
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.post(
    "/{post_id}/images",
    response_model=BlogPostRead,
    dependencies=[Depends(get_current_admin)],
)
async def add_post_images(
    post_id: int,
    files: List[UploadFile],
    session: Session = Depends(get_session),
):
    post = _get_post_or_404(post_id, session)

    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded files must all be images",
            )

    for file in files:
        image_bytes = await file.read()
        secure_url, public_id = cloudinary_service.upload_blog_image(image_bytes)
        session.add(
            BlogPostImage(blog_post_id=post.id, image_url=secure_url, public_id=public_id)
        )

    session.commit()
    session.refresh(post)
    return post


@router.post(
    "/{post_id}/images/generate",
    response_model=BlogPostRead,
    dependencies=[Depends(get_current_admin)],
)
def generate_post_image(
    post_id: int,
    payload: GenerateBlogImageRequest,
    session: Session = Depends(get_session),
):
    post = _get_post_or_404(post_id, session)

    image_bytes = openai_service.generate_blog_image(payload.prompt)
    secure_url, public_id = cloudinary_service.upload_blog_image(image_bytes)

    session.add(BlogPostImage(blog_post_id=post.id, image_url=secure_url, public_id=public_id))
    session.commit()
    session.refresh(post)
    return post


@router.delete(
    "/{post_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_post_image(post_id: int, image_id: int, session: Session = Depends(get_session)):
    _get_post_or_404(post_id, session)
    image = _get_post_image_or_404(post_id, image_id, session)

    cloudinary_service.delete_image(image.public_id)
    session.delete(image)
    session.commit()


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_post(post_id: int, session: Session = Depends(get_session)):
    post = _get_post_or_404(post_id, session)

    cloudinary_service.delete_image(post.featured_image_public_id)
    for image in post.images:
        cloudinary_service.delete_image(image.public_id)

    session.delete(post)
    session.commit()
