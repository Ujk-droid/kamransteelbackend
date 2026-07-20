from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_admin
from app.models.faq import FAQ
from app.schemas.faq import AskRequest, AskResponse, FAQCreate, FAQRead, FAQUpdate
from app.services import faq_matching

router = APIRouter(prefix="/faqs", tags=["faqs"])


def _get_faq_or_404(faq_id: int, session: Session) -> FAQ:
    faq = session.get(FAQ, faq_id)
    if faq is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    return faq


def _ordered_faqs(session: Session) -> List[FAQ]:
    query = select(FAQ).order_by(FAQ.display_order, FAQ.id)
    return session.exec(query).all()


@router.get("", response_model=List[FAQRead])
def list_faqs(session: Session = Depends(get_session)):
    return _ordered_faqs(session)


@router.post("/ask", response_model=AskResponse)
def ask_faq(payload: AskRequest, session: Session = Depends(get_session)):
    faqs = _ordered_faqs(session)
    return faq_matching.find_best_match(payload.message, faqs)


@router.get(
    "/admin",
    response_model=List[FAQRead],
    dependencies=[Depends(get_current_admin)],
)
def list_all_faqs(session: Session = Depends(get_session)):
    return _ordered_faqs(session)


@router.post(
    "",
    response_model=FAQRead,
    dependencies=[Depends(get_current_admin)],
)
def create_faq(payload: FAQCreate, session: Session = Depends(get_session)):
    faq = FAQ(**payload.model_dump())
    session.add(faq)
    session.commit()
    session.refresh(faq)
    return faq


@router.patch(
    "/{faq_id}",
    response_model=FAQRead,
    dependencies=[Depends(get_current_admin)],
)
def update_faq(faq_id: int, payload: FAQUpdate, session: Session = Depends(get_session)):
    faq = _get_faq_or_404(faq_id, session)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(faq, field, value)

    session.add(faq)
    session.commit()
    session.refresh(faq)
    return faq


@router.delete(
    "/{faq_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_faq(faq_id: int, session: Session = Depends(get_session)):
    faq = _get_faq_or_404(faq_id, session)
    session.delete(faq)
    session.commit()
