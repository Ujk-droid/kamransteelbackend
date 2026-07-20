from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.core.database import get_session
from app.core.security import get_current_admin
from app.models.blog_post import BlogPost, PostStatus
from app.models.contact_message import ContactMessage
from app.models.estimate import Estimate
from app.models.faq import FAQ
from app.models.product import Product
from app.models.review import Review, ReviewStatus
from app.schemas.dashboard import (
    BlogPostSummary,
    ContactMessageSummary,
    DashboardSummary,
    EstimateDailyCount,
    EstimateSummary,
    FAQSummary,
    ProductSummary,
    ReviewSummary,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    dependencies=[Depends(get_current_admin)],
)
def get_dashboard_summary(session: Session = Depends(get_session)):
    contact_total = session.exec(select(func.count()).select_from(ContactMessage)).one()
    contact_unread = session.exec(
        select(func.count()).select_from(ContactMessage).where(ContactMessage.is_read == False)  # noqa: E712
    ).one()

    review_total = session.exec(select(func.count()).select_from(Review)).one()
    review_pending = session.exec(
        select(func.count()).select_from(Review).where(Review.status == ReviewStatus.PENDING)
    ).one()
    review_approved = session.exec(
        select(func.count()).select_from(Review).where(Review.status == ReviewStatus.APPROVED)
    ).one()
    review_rejected = session.exec(
        select(func.count()).select_from(Review).where(Review.status == ReviewStatus.REJECTED)
    ).one()

    product_total = session.exec(select(func.count()).select_from(Product)).one()
    category_rows = session.exec(
        select(Product.category, func.count()).group_by(Product.category)
    ).all()
    by_category = {
        (category.value if hasattr(category, "value") else category): count
        for category, count in category_rows
    }

    blog_total = session.exec(select(func.count()).select_from(BlogPost)).one()
    blog_published = session.exec(
        select(func.count()).select_from(BlogPost).where(BlogPost.status == PostStatus.PUBLISHED)
    ).one()
    blog_draft = blog_total - blog_published

    estimate_total = session.exec(select(func.count()).select_from(Estimate)).one()

    today = datetime.now(timezone.utc).date()
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    daily_rows = session.exec(
        select(func.date(Estimate.created_at), func.count())
        .where(Estimate.created_at >= thirty_days_ago)
        .group_by(func.date(Estimate.created_at))
    ).all()
    counts_by_date = {str(day): count for day, count in daily_rows}
    daily_counts = [
        EstimateDailyCount(
            date=str(today - timedelta(days=offset)),
            count=counts_by_date.get(str(today - timedelta(days=offset)), 0),
        )
        for offset in range(29, -1, -1)
    ]

    faq_total = session.exec(select(func.count()).select_from(FAQ)).one()

    return DashboardSummary(
        contact_messages=ContactMessageSummary(total=contact_total, unread=contact_unread),
        reviews=ReviewSummary(
            total=review_total,
            pending=review_pending,
            approved=review_approved,
            rejected=review_rejected,
        ),
        products=ProductSummary(total=product_total, by_category=by_category),
        blog_posts=BlogPostSummary(total=blog_total, published=blog_published, draft=blog_draft),
        estimates=EstimateSummary(total=estimate_total, daily_counts=daily_counts),
        faqs=FAQSummary(total=faq_total),
    )
