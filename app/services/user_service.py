from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.exceptions import NotFoundError


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_profile(self, user_id: str) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    def update_profile(self, user_id: str, display_name: str | None) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if display_name:
            user.display_name = display_name
        self.user_repo.db.commit()
        self.user_repo.db.refresh(user)
        return user
