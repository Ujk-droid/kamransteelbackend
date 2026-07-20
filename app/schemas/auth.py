from pydantic import BaseModel


class GoogleLoginRequest(BaseModel):
    """Sent by the frontend after Google's sign-in popup returns an ID token."""

    id_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminProfile(BaseModel):
    email: str
