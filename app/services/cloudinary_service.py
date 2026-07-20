import re
from typing import Optional, Tuple

import cloudinary.uploader

from app.core import cloudinary_client  # noqa: F401 - runs cloudinary.config() on import


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "uncategorized"


def upload_image(file_bytes: bytes, category: str) -> Tuple[str, str]:
    """Uploads image bytes to Cloudinary under a category-named folder.

    Returns (secure_url, public_id).
    """
    folder = f"kamransteelworks/estimates/{_slugify(category)}"
    result = cloudinary.uploader.upload(file_bytes, folder=folder, resource_type="image")
    return result["secure_url"], result["public_id"]


def delete_image(public_id: Optional[str]) -> None:
    if not public_id:
        return
    cloudinary.uploader.destroy(public_id)


def upload_product_image(file_bytes: bytes, category: str) -> Tuple[str, str]:
    """Uploads a product gallery image to Cloudinary under a category-named folder.

    Returns (secure_url, public_id).
    """
    folder = f"kamransteelworks/products/{_slugify(category)}"
    result = cloudinary.uploader.upload(file_bytes, folder=folder, resource_type="image")
    return result["secure_url"], result["public_id"]


def upload_client_project_image(file_bytes: bytes, category: str) -> Tuple[str, str]:
    """Uploads a client project gallery image to Cloudinary under a category-named folder.

    Returns (secure_url, public_id).
    """
    folder = f"kamransteelworks/client-projects/{_slugify(category)}"
    result = cloudinary.uploader.upload(file_bytes, folder=folder, resource_type="image")
    return result["secure_url"], result["public_id"]


def upload_blog_image(file_bytes: bytes) -> Tuple[str, str]:
    """Uploads a blog post's featured image to Cloudinary.

    Returns (secure_url, public_id).
    """
    result = cloudinary.uploader.upload(
        file_bytes, folder="kamransteelworks/blogs", resource_type="image"
    )
    return result["secure_url"], result["public_id"]
