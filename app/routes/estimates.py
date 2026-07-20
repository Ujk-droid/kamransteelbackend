from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import Response
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_admin
from app.models.estimate import Estimate
from app.schemas.estimate import (
    EstimateCreate,
    EstimateExtraction,
    EstimateRead,
    GenerateImageRequest,
)
from app.services import cloudinary_service, openai_service, pdf_service

router = APIRouter(
    prefix="/estimates", tags=["estimates"], dependencies=[Depends(get_current_admin)]
)


def _get_estimate_or_404(estimate_id: int, session: Session) -> Estimate:
    estimate = session.get(Estimate, estimate_id)
    if estimate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estimate not found")
    return estimate


@router.post("", response_model=EstimateRead)
def create_estimate(payload: EstimateCreate, session: Session = Depends(get_session)):
    estimate = Estimate(**payload.model_dump())
    session.add(estimate)
    session.commit()
    session.refresh(estimate)
    return estimate


@router.post("/extract", response_model=EstimateExtraction)
async def extract_estimate_from_note(file: UploadFile):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be an image"
        )

    image_bytes = await file.read()
    data = openai_service.extract_estimate_from_image(image_bytes)

    try:
        return EstimateExtraction(**{k: v for k, v in data.items() if k in EstimateExtraction.model_fields})
    except ValidationError:
        return EstimateExtraction()


@router.get("", response_model=List[EstimateRead])
def list_estimates(session: Session = Depends(get_session)):
    return session.exec(select(Estimate).order_by(Estimate.created_at.desc())).all()


@router.get("/{estimate_id}", response_model=EstimateRead)
def get_estimate(estimate_id: int, session: Session = Depends(get_session)):
    return _get_estimate_or_404(estimate_id, session)


@router.put("/{estimate_id}", response_model=EstimateRead)
def update_estimate(
    estimate_id: int, payload: EstimateCreate, session: Session = Depends(get_session)
):
    estimate = _get_estimate_or_404(estimate_id, session)
    for field, value in payload.model_dump().items():
        setattr(estimate, field, value)
    session.add(estimate)
    session.commit()
    session.refresh(estimate)
    return estimate


@router.delete("/{estimate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_estimate(estimate_id: int, session: Session = Depends(get_session)):
    estimate = _get_estimate_or_404(estimate_id, session)
    cloudinary_service.delete_image(estimate.image_public_id)
    session.delete(estimate)
    session.commit()


@router.post("/{estimate_id}/image/generate", response_model=EstimateRead)
def generate_estimate_image(
    estimate_id: int,
    payload: GenerateImageRequest,
    session: Session = Depends(get_session),
):
    estimate = _get_estimate_or_404(estimate_id, session)

    image_bytes = openai_service.generate_estimate_image(
        category=estimate.category,
        size=estimate.size,
        color=estimate.color,
        material=estimate.material,
        custom_prompt=payload.custom_prompt,
    )

    cloudinary_service.delete_image(estimate.image_public_id)
    secure_url, public_id = cloudinary_service.upload_image(image_bytes, estimate.category)

    estimate.image_url = secure_url
    estimate.image_public_id = public_id
    session.add(estimate)
    session.commit()
    session.refresh(estimate)
    return estimate


@router.post("/{estimate_id}/image/upload", response_model=EstimateRead)
async def upload_estimate_image(
    estimate_id: int,
    file: UploadFile,
    session: Session = Depends(get_session),
):
    estimate = _get_estimate_or_404(estimate_id, session)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be an image"
        )

    image_bytes = await file.read()

    cloudinary_service.delete_image(estimate.image_public_id)
    secure_url, public_id = cloudinary_service.upload_image(image_bytes, estimate.category)

    estimate.image_url = secure_url
    estimate.image_public_id = public_id
    session.add(estimate)
    session.commit()
    session.refresh(estimate)
    return estimate


@router.get("/{estimate_id}/pdf")
def download_estimate_pdf(
    estimate_id: int,
    theme: Literal["dark", "light"] = "dark",
    session: Session = Depends(get_session),
):
    estimate = _get_estimate_or_404(estimate_id, session)
    pdf_bytes = pdf_service.render_estimate_pdf(estimate, theme=theme)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="estimate-{estimate_id}-{theme}.pdf"'
        },
    )
