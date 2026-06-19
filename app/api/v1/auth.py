from fastapi import APIRouter, Depends, status

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, LogoutRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.models.user import User
from app.api.deps import get_auth_service, get_current_user

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
def logout_all(current_user: User = Depends(get_current_user), auth: AuthService = Depends(get_auth_service)):
    auth.logout_all(current_user.id)
