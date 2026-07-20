# Kamran Steel Works — Backend

FastAPI backend for the Kamran Steel Works business website. Single admin (Google OAuth login), PostgreSQL database via SQLModel, migrations via Alembic.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Install the system libraries WeasyPrint needs to render PDFs (one-time, Linux/Docker):
   ```bash
   sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libcairo2 libffi-dev
   ```

3. Copy the environment template and fill in real values:
   ```bash
   cp .env.example .env
   ```
   You'll need:
   - A running PostgreSQL database and its connection string (`DATABASE_URL`)
   - A random secret for `JWT_SECRET_KEY` (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`)
   - A Google OAuth Client ID/Secret from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Your admin Gmail address(es) as `ADMIN_GMAIL_ADDRESSES` — a comma-separated allow-list of the only accounts allowed to log in
   - Cloudinary credentials (image storage) and an OpenAI API key with image-generation access (used by the Estimate feature)
   - Mailtrap and Hugging Face credentials (only needed once those features are built)

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the dev server:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Open the interactive API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Project layout

- `app/main.py` — creates the FastAPI app and wires up routes
- `app/core/` — settings (`config.py`), database connection (`database.py`), auth logic (`security.py`)
- `app/models/` — SQLModel database table definitions
- `app/schemas/` — request/response JSON shapes
- `app/routes/` — API endpoints, grouped by resource
- `alembic/` — database migration scripts

## Authentication

There is no public signup. The frontend uses Google Sign-In to get a Google ID token, then calls `POST /auth/google` with it. The backend verifies the token with Google, checks that the email is in the `ADMIN_GMAIL_ADDRESSES` allow-list, and — only then — issues a JWT. That JWT is sent as `Authorization: Bearer <token>` on subsequent admin-only requests (e.g. `GET /contact`).

## Estimates (admin-only PDF quotes)

`app/routes/estimates.py` lets the admin build a priced estimate and download it as a styled PDF:

1. `POST /estimates` — save the spec (category, size, color, material, cost, payment schedule %). No image yet.
2. Either `POST /estimates/{id}/image/generate` (OpenAI creates a product photo from the spec) or `POST /estimates/{id}/image/upload` (admin uploads their own file). Either way the image is stored in Cloudinary under `kamransteelworks/estimates/<category>/`, and replacing an image deletes the old Cloudinary file.
3. `GET /estimates/{id}/pdf` — renders `app/templates/estimate_pdf.html` (dark charcoal + gold theme, logo embedded from `logo.png` at the project root) via WeasyPrint and streams back a downloadable PDF.

All of these routes require the admin JWT. The three payment percentages must sum to 100 (validated in `app/schemas/estimate.py`); Rupee amounts per payment stage are computed on the fly from `cost`, never stored, so they can't go stale.

`app/services/` holds the three external integrations (`cloudinary_service.py`, `openai_service.py`, `pdf_service.py`) so the route file itself just wires things together.

## Adding a new resource

The `contact_message` model/schema/route trio is a template. To add something like "Products": create `app/models/product.py`, `app/schemas/product.py`, `app/routes/products.py` following the same pattern, register the router in `app/main.py`, then run:
```bash
alembic revision --autogenerate -m "add product table"
alembic upgrade head
```
