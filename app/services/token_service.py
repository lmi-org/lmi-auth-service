from app.core.exceptions import CredentialsError
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository


class TokenService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_current_user(self, token: str):
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise CredentialsError("Invalid or expired access token")

        user = self.user_repo.get_by_id(payload["sub"])
        if not user:
            raise CredentialsError("User not found")

        return user
