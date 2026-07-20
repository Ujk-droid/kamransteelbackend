from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_admin
from app.models.client_project import ClientProject, ClientProjectImage
from app.schemas.client_project import (
    ClientProjectCreate,
    ClientProjectRead,
    ClientProjectUpdate,
)
from app.services import cloudinary_service

router = APIRouter(prefix="/client-projects", tags=["client-projects"])


def _normalize_category(category: str) -> str:
    return category.strip().lower()


def _get_client_project_or_404(client_project_id: int, session: Session) -> ClientProject:
    client_project = session.get(ClientProject, client_project_id)
    if client_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client project not found"
        )
    return client_project


def _get_client_project_image_or_404(
    client_project_id: int, image_id: int, session: Session
) -> ClientProjectImage:
    image = session.get(ClientProjectImage, image_id)
    if image is None or image.client_project_id != client_project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client project image not found"
        )
    return image


@router.get("", response_model=List[ClientProjectRead])
def list_client_projects(
    category: Optional[str] = None, session: Session = Depends(get_session)
):
    query = select(ClientProject).order_by(ClientProject.created_at.desc())
    if category is not None:
        query = query.where(ClientProject.category == _normalize_category(category))
    return session.exec(query).all()


@router.get("/{client_project_id}", response_model=ClientProjectRead)
def get_client_project(client_project_id: int, session: Session = Depends(get_session)):
    return _get_client_project_or_404(client_project_id, session)


@router.post(
    "",
    response_model=ClientProjectRead,
    dependencies=[Depends(get_current_admin)],
)
def create_client_project(
    payload: ClientProjectCreate, session: Session = Depends(get_session)
):
    data = payload.model_dump()
    data["category"] = _normalize_category(data["category"])
    client_project = ClientProject(**data)
    session.add(client_project)
    session.commit()
    session.refresh(client_project)
    return client_project


@router.patch(
    "/{client_project_id}",
    response_model=ClientProjectRead,
    dependencies=[Depends(get_current_admin)],
)
def update_client_project(
    client_project_id: int,
    payload: ClientProjectUpdate,
    session: Session = Depends(get_session),
):
    client_project = _get_client_project_or_404(client_project_id, session)

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "category":
            value = _normalize_category(value)
        setattr(client_project, field, value)

    session.add(client_project)
    session.commit()
    session.refresh(client_project)
    return client_project


@router.post(
    "/{client_project_id}/images",
    response_model=ClientProjectRead,
    dependencies=[Depends(get_current_admin)],
)
async def add_client_project_images(
    client_project_id: int,
    files: List[UploadFile],
    session: Session = Depends(get_session),
):
    client_project = _get_client_project_or_404(client_project_id, session)

    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded files must all be images",
            )

    for file in files:
        image_bytes = await file.read()
        secure_url, public_id = cloudinary_service.upload_client_project_image(
            image_bytes, client_project.category
        )
        session.add(
            ClientProjectImage(
                client_project_id=client_project.id, image_url=secure_url, public_id=public_id
            )
        )

    session.commit()
    session.refresh(client_project)
    return client_project


@router.delete(
    "/{client_project_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_client_project_image(
    client_project_id: int, image_id: int, session: Session = Depends(get_session)
):
    _get_client_project_or_404(client_project_id, session)
    image = _get_client_project_image_or_404(client_project_id, image_id, session)

    cloudinary_service.delete_image(image.public_id)
    session.delete(image)
    session.commit()


@router.delete(
    "/{client_project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_client_project(client_project_id: int, session: Session = Depends(get_session)):
    client_project = _get_client_project_or_404(client_project_id, session)

    for image in client_project.images:
        cloudinary_service.delete_image(image.public_id)

    session.delete(client_project)
    session.commit()
