from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_admin
from app.models.product import Product, ProductImage
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services import cloudinary_service

router = APIRouter(prefix="/products", tags=["products"])


def _normalize_category(category: str) -> str:
    return category.strip().lower()


def _get_product_or_404(product_id: int, session: Session) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def _get_product_image_or_404(product_id: int, image_id: int, session: Session) -> ProductImage:
    image = session.get(ProductImage, image_id)
    if image is None or image.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product image not found"
        )
    return image


@router.get("", response_model=List[ProductRead])
def list_products(
    category: Optional[str] = None, session: Session = Depends(get_session)
):
    query = select(Product).order_by(Product.created_at.desc())
    if category is not None:
        query = query.where(Product.category == _normalize_category(category))
    return session.exec(query).all()


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    return _get_product_or_404(product_id, session)


@router.post(
    "",
    response_model=ProductRead,
    dependencies=[Depends(get_current_admin)],
)
def create_product(payload: ProductCreate, session: Session = Depends(get_session)):
    data = payload.model_dump()
    data["category"] = _normalize_category(data["category"])
    product = Product(**data)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(get_current_admin)],
)
def update_product(
    product_id: int, payload: ProductUpdate, session: Session = Depends(get_session)
):
    product = _get_product_or_404(product_id, session)

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "category":
            value = _normalize_category(value)
        setattr(product, field, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.post(
    "/{product_id}/images",
    response_model=ProductRead,
    dependencies=[Depends(get_current_admin)],
)
async def add_product_images(
    product_id: int,
    files: List[UploadFile],
    session: Session = Depends(get_session),
):
    product = _get_product_or_404(product_id, session)

    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded files must all be images",
            )

    for file in files:
        image_bytes = await file.read()
        secure_url, public_id = cloudinary_service.upload_product_image(
            image_bytes, product.category
        )
        session.add(
            ProductImage(product_id=product.id, image_url=secure_url, public_id=public_id)
        )

    session.commit()
    session.refresh(product)
    return product


@router.delete(
    "/{product_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_product_image(product_id: int, image_id: int, session: Session = Depends(get_session)):
    _get_product_or_404(product_id, session)
    image = _get_product_image_or_404(product_id, image_id, session)

    cloudinary_service.delete_image(image.public_id)
    session.delete(image)
    session.commit()


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = _get_product_or_404(product_id, session)

    for image in product.images:
        cloudinary_service.delete_image(image.public_id)

    session.delete(product)
    session.commit()
