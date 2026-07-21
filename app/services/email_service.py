import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.models.contact_message import ContactMessage
from app.models.review import Review

logger = logging.getLogger(__name__)


def _send_email(subject: str, text_body: str, html_body: str) -> None:
    """Sends an email to the admin via SMTP.

    Never raises: any failure is logged and swallowed so callers can fire-and-forget.
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"Kamran Steel Works <{settings.SMTP_USERNAME}>"
    message["To"] = ", ".join(settings.admin_emails)
    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
    except Exception:
        logger.exception("Failed to send email: %s", subject)


def send_new_contact_message_email(contact_message: ContactMessage) -> None:
    subject = f"New Contact Message from {contact_message.name}"

    text_body = (
        f"New contact message received.\n\n"
        f"Name: {contact_message.name}\n"
        f"Email: {contact_message.email}\n"
        f"Message:\n{contact_message.message}\n"
    )

    html_body = f"""
    <html>
      <body>
        <h2>New Contact Message</h2>
        <p><strong>Name:</strong> {contact_message.name}</p>
        <p><strong>Email:</strong> {contact_message.email}</p>
        <p><strong>Message:</strong></p>
        <p>{contact_message.message}</p>
      </body>
    </html>
    """

    _send_email(subject, text_body, html_body)


def send_new_review_email(review: Review, was_auto_rejected: bool) -> None:
    status_text = (
        "Auto-rejected by profanity filter" if was_auto_rejected else "Pending approval"
    )
    subject = f"New Review Submitted ({status_text})"

    text_body = (
        f"New review received.\n\n"
        f"Client: {review.client_name}\n"
        f"Rating: {review.rating}/5\n"
        f"Review:\n{review.review_text}\n\n"
        f"Status: {status_text}\n"
    )

    html_body = f"""
    <html>
      <body>
        <h2>New Review Submitted</h2>
        <p><strong>Client:</strong> {review.client_name}</p>
        <p><strong>Rating:</strong> {review.rating}/5</p>
        <p><strong>Review:</strong></p>
        <p>{review.review_text}</p>
        <p><strong>Status:</strong> {status_text}</p>
      </body>
    </html>
    """

    _send_email(subject, text_body, html_body)
