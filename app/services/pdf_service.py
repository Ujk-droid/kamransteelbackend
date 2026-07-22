import base64
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.models.estimate import Estimate
from app.schemas.estimate import EstimateRead

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
LOGO_PATH = PROJECT_ROOT / "frontend" / "public" / "logo.png"

_DARK_THEME = {
    "background": "#1c1c1c",
    "text_primary": "#e8e4da",
    "text_strong": "#ffffff",
    "text_muted": "#b9b3a2",
    "text_faint": "#7a7568",
    "accent": "#c9a227",
    "border_strong": "#3a3a3a",
    "border_faint": "#302f2a",
    "row_alt_bg": "#232323",
}

_LIGHT_THEME = {
    "background": "#ffffff",
    "text_primary": "#1c1c1c",
    "text_strong": "#1a1a1a",
    "text_muted": "#5a5648",
    "text_faint": "#8a8578",
    "accent": "#c9a227",
    "border_strong": "#d8d4c8",
    "border_faint": "#e6e2d6",
    "row_alt_bg": "#f7f5ef",
}

COMPANY_NAME = "Kamran Steel Works"
COMPANY_ADDRESS = (
    "Shop # 52, Gul-e-Rana Colony, Abro Road, Street #3, "
    "Near Agha Khan School, Solder Bazar No-1, Karachi"
)
COMPANY_PHONE = "0300-2882134 / 0345-6167188"
COMPANY_WEBSITE = "kamransteelfrontend.vercel.app"
COMPANY_WHATSAPP = "0345-6167188"
COMPANY_EMAIL = "kamransteelw@gmail.com"

_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def _logo_data_uri() -> str:
    logo_bytes = LOGO_PATH.read_bytes()
    encoded = base64.b64encode(logo_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _money(value) -> str:
    return f"{value:,.2f}"


def render_estimate_pdf(estimate: Estimate, theme: str = "dark") -> bytes:
    estimate_read = EstimateRead.model_validate(estimate)
    colors = _LIGHT_THEME if theme == "light" else _DARK_THEME

    template = _env.get_template("estimate_pdf.html")
    html_content = template.render(
        colors=colors,
        company_name=COMPANY_NAME,
        company_address=COMPANY_ADDRESS,
        company_phone=COMPANY_PHONE,
        company_website=COMPANY_WEBSITE,
        company_whatsapp=COMPANY_WHATSAPP,
        company_email=COMPANY_EMAIL,
        logo_base64=_logo_data_uri(),
        estimate_id=estimate_read.id,
        created_at=estimate_read.created_at.strftime("%B %d, %Y"),
        category=estimate_read.category,
        size=estimate_read.size,
        color=estimate_read.color,
        material=estimate_read.material,
        cost=_money(estimate_read.cost),
        extra_specs=estimate_read.extra_specs,
        image_url=estimate_read.image_url,
        advance_percent=estimate_read.advance_percent,
        mid_percent=estimate_read.mid_percent,
        final_percent=estimate_read.final_percent,
        advance_amount=_money(estimate_read.advance_amount),
        mid_amount=_money(estimate_read.mid_amount),
        final_amount=_money(estimate_read.final_amount),
    )

    return HTML(string=html_content, base_url=str(PROJECT_ROOT)).write_pdf()
