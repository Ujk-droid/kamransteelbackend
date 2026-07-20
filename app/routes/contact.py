from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_admin
from app.models.contact_message import ContactMessage
from app.schemas.contact_message import ContactMessageCreate, ContactMessageRead
from app.services import email_service

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("", response_model=ContactMessageRead)
def submit_contact_message(
    payload: ContactMessageCreate, session: Session = Depends(get_session)
):
    """Public endpoint: anyone visiting the website can submit the contact form."""
    contact_message = ContactMessage(**payload.model_dump())
    session.add(contact_message)
    session.commit()
    session.refresh(contact_message)
    email_service.send_new_contact_message_email(contact_message)
    return contact_message


@router.get("", response_model=List[ContactMessageRead])
def list_contact_messages(
    session: Session = Depends(get_session),
    current_admin_email: str = Depends(get_current_admin),
):
    """Admin-only endpoint: view all contact form submissions."""
    return session.exec(select(ContactMessage).order_by(ContactMessage.created_at.desc())).all()


@router.patch("/{message_id}/read", response_model=ContactMessageRead)
def mark_contact_message_read(
    message_id: int,
    session: Session = Depends(get_session),
    current_admin_email: str = Depends(get_current_admin),
):
    """Admin-only endpoint: mark a contact message as read."""
    contact_message = session.get(ContactMessage, message_id)
    if contact_message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact message not found")

    contact_message.is_read = True
    session.add(contact_message)
    session.commit()
    session.refresh(contact_message)
    return contact_message
