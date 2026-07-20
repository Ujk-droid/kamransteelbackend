from pydantic import BaseModel


class ContactMessageSummary(BaseModel):
    total: int
    unread: int


class ReviewSummary(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int


class ProductSummary(BaseModel):
    total: int
    by_category: dict[str, int]


class BlogPostSummary(BaseModel):
    total: int
    published: int
    draft: int


class EstimateDailyCount(BaseModel):
    date: str
    count: int


class EstimateSummary(BaseModel):
    total: int
    daily_counts: list[EstimateDailyCount] = []


class FAQSummary(BaseModel):
    total: int


class DashboardSummary(BaseModel):
    contact_messages: ContactMessageSummary
    reviews: ReviewSummary
    products: ProductSummary
    blog_posts: BlogPostSummary
    estimates: EstimateSummary
    faqs: FAQSummary
