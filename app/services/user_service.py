from app.core.exceptions import NotFoundError
from app.models.user import User
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository):
        self.user_repo = user_repo
        self.session_repo = session_repo

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

    def delete_account(self, user_id: str) -> None:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        self.session_repo.delete_user_sessions(user_id)
        self.user_repo.delete_by_id(user_id)
