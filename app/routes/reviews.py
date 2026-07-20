from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_admin
from app.models.review import Review, ReviewStatus
from app.schemas.review import ReviewCreate, ReviewRead
from app.services import email_service, profanity_filter

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _get_review_or_404(review_id: int, session: Session) -> Review:
    review = session.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review


def _set_status(review_id: int, new_status: ReviewStatus, session: Session) -> Review:
    review = _get_review_or_404(review_id, session)
    review.status = new_status
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


@router.post("", response_model=ReviewRead)
def create_review(payload: ReviewCreate, session: Session = Depends(get_session)):
    is_flagged = profanity_filter.contains_profanity(
        payload.review_text
    ) or profanity_filter.contains_profanity(payload.client_name)

    review = Review(
        **payload.model_dump(),
        status=ReviewStatus.REJECTED if is_flagged else ReviewStatus.PENDING,
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    email_service.send_new_review_email(review, was_auto_rejected=is_flagged)
    return review


@router.get("", response_model=List[ReviewRead])
def list_approved_reviews(session: Session = Depends(get_session)):
    query = (
        select(Review)
        .where(Review.status == ReviewStatus.APPROVED)
        .order_by(Review.created_at.desc())
    )
    return session.exec(query).all()


@router.get(
    "/admin",
    response_model=List[ReviewRead],
    dependencies=[Depends(get_current_admin)],
)
def list_all_reviews(session: Session = Depends(get_session)):
    return session.exec(select(Review).order_by(Review.created_at.desc())).all()


@router.post(
    "/{review_id}/approve",
    response_model=ReviewRead,
    dependencies=[Depends(get_current_admin)],
)
def approve_review(review_id: int, session: Session = Depends(get_session)):
    return _set_status(review_id, ReviewStatus.APPROVED, session)


@router.post(
    "/{review_id}/reject",
    response_model=ReviewRead,
    dependencies=[Depends(get_current_admin)],
)
def reject_review(review_id: int, session: Session = Depends(get_session)):
    return _set_status(review_id, ReviewStatus.REJECTED, session)


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_review(review_id: int, session: Session = Depends(get_session)):
    review = _get_review_or_404(review_id, session)
    session.delete(review)
    session.commit()
