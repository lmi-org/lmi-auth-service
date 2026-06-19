from fastapi import APIRouter, Depends

from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.models.user import User
from app.api.deps import get_user_service, get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me")
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return UserResponse.model_validate(current_user)


@router.patch("/me")
def update_profile(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    user = user_service.update_profile(current_user.id, body.display_name)
    return UserResponse.model_validate(user)

@router.delete("/me", status_code=204)
def delete_account(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    user_service.delete_account(current_user.id)