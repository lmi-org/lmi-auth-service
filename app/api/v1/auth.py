from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RequestVerificationResponse,
    TokenResponse,
    VerifyEmailRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, auth: AuthService = Depends(get_auth_service)):
    user = auth.register(body.email, body.username, body.password, body.display_name)
    return {"message": "User registered successfully", "user_id": user.id}


@router.post("/login")
def login(body: LoginRequest, auth: AuthService = Depends(get_auth_service)):
    access_token, refresh_token, user = auth.login(body.email, body.password)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, expires_in=900)


@router.post("/refresh")
def refresh(body: RefreshRequest, auth: AuthService = Depends(get_auth_service)):
    access_token, refresh_token = auth.refresh(body.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, expires_in=900)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(body: LogoutRequest, auth: AuthService = Depends(get_auth_service)):
    auth.logout(body.refresh_token)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all(
    current_user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    auth.logout_all(current_user.id)


@router.post("/request-verification")
def request_verification(
    current_user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    token = auth.request_verification(current_user.id)
    return RequestVerificationResponse(message="Verification email sent", token=token)


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(body: VerifyEmailRequest, auth: AuthService = Depends(get_auth_service)):
    auth.verify_email(body.token)
    return {"message": "Email verified successfully"}
