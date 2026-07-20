from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import (
    auth,
    blog_posts,
    categories,
    client_projects,
    contact,
    dashboard,
    estimates,
    faqs,
    products,
    reviews,
)

app = FastAPI(
    title="Kamran Steel Works API",
    description="Backend API for the Kamran Steel Works business website.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(contact.router)
app.include_router(estimates.router)
app.include_router(products.router)
app.include_router(client_projects.router)
app.include_router(blog_posts.router)
app.include_router(faqs.router)
app.include_router(reviews.router)
app.include_router(categories.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
