from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DATABASE_URL: str

    # JWT (our own login tokens, issued after Google verifies the admin)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # AI features (used by future endpoints)
    OPENAI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""

    # Cloudinary (image hosting, used by future endpoints)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Mailtrap (email sending, used by future endpoints)
    MAILTRAP_HOST: str = ""
    MAILTRAP_PORT: int = 2525
    MAILTRAP_USERNAME: str = ""
    MAILTRAP_PASSWORD: str = ""

    # Google OAuth (admin login)
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str = ""

    # Comma-separated list of Gmail addresses allowed to authenticate as admin
    ADMIN_GMAIL_ADDRESSES: str

    # Comma-separated list of frontend origins allowed to call this API
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def admin_emails(self) -> set[str]:
        return {email.strip().lower() for email in self.ADMIN_GMAIL_ADDRESSES.split(",") if email.strip()}

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
