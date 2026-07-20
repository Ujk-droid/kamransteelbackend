import base64
import json
from typing import Optional

from openai import OpenAI

from app.core.config import settings

_client = OpenAI(api_key=settings.OPENAI_API_KEY)

_EXTRACTION_SYSTEM_PROMPT = (
    "You read handwritten estimate notes for a custom steel fabrication shop. "
    "Extract these fields if legible: category (must be exactly one of: gate, stairs, "
    "windows, shutters, grills, doors), size, color, material, cost (a plain number, "
    "no currency symbols or commas). "
    "If the note contains additional details that don't fit those fields — separate "
    "length/width/height, quantity, extra notes, etc. — extract each as a "
    '{"label": ..., "value": ...} pair in an "extra_specs" array, without duplicating '
    "anything already captured in the main fields. "
    'Return a JSON object with exactly these keys: "category", "size", "color", '
    '"material", "cost", "extra_specs". Use null for any main field you cannot '
    "confidently read, and an empty array for extra_specs if there's nothing extra."
)


def _build_prompt(category: str, size: str, color: str, material: str) -> str:
    return (
        f"A professional, high-quality product photograph of a custom-fabricated "
        f"steel {category}, size {size}, color {color}, made of {material}. "
        f"Clean studio lighting, plain neutral background, sharp focus, realistic, "
        f"industrial catalog style, no text or watermarks."
    )


def generate_estimate_image(
    category: str,
    size: str,
    color: str,
    material: str,
    custom_prompt: Optional[str] = None,
) -> bytes:
    """Generates a product image via OpenAI and returns the raw image bytes."""
    prompt = custom_prompt or _build_prompt(category, size, color, material)

    response = _client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )

    b64_data = response.data[0].b64_json
    return base64.b64decode(b64_data)


def generate_blog_image(prompt: str) -> bytes:
    """Generates a blog image via OpenAI from a free-form prompt and returns the raw bytes."""
    response = _client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )

    b64_data = response.data[0].b64_json
    return base64.b64decode(b64_data)


def extract_estimate_from_image(image_bytes: bytes) -> dict:
    """Reads a photo of a handwritten estimate note and returns whatever fields
    the model could confidently make out, as a plain dict (missing/unreadable
    fields are simply absent or null)."""
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = _client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract the estimate details from this handwritten note."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            },
        ],
    )

    try:
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, TypeError):
        return {}
