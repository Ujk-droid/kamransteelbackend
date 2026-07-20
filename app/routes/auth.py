from fastapi import APIRouter, Depends

from app.core.security import create_access_token, get_current_admin, verify_google_id_token
from app.schemas.auth import AdminProfile, GoogleLoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=TokenResponse)
def login_with_google(payload: GoogleLoginRequest):
    """Verify a Google ID token and, if it belongs to the admin, issue our own JWT."""
    email = verify_google_id_token(payload.id_token)
    access_token = create_access_token(email)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=AdminProfile)
def read_current_admin(current_admin_email: str = Depends(get_current_admin)):
    return AdminProfile(email=current_admin_email)
