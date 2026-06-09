from datetime import datetime, timedelta, timezone

from app.core.security import (
    hash_password,
    verify_password,
    hash_token,
    generate_jti,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import CredentialsError, ConflictError
from app.models.user import User
from app.models.session import Session as SessionModel
from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository


class AuthService:
    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository):
        self.user_repo = user_repo
        self.session_repo = session_repo

    def register(self, email: str, username: str, password: str, display_name: str) -> User:
        if self.user_repo.get_by_email(email):
            raise ConflictError("Email already registered")
        if self.user_repo.get_by_username(username):
            raise ConflictError("Username already taken")

        user = User(
            email=email,
            username=username,
            display_name=display_name,
            hashed_password=hash_password(password),
        )
        return self.user_repo.create(user)

    def login(self, email: str, password: str) -> tuple[str, str, User]:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise CredentialsError("Invalid email or password")

        session_id = generate_jti()
        access_token = create_access_token(subject=user.id, jti=session_id)
        refresh_token = create_refresh_token(subject=user.id, jti=session_id)

        session = SessionModel(
            id=session_id,
            user_id=user.id,
            refresh_token_hash=hash_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        self.session_repo.create(session)

        return access_token, refresh_token, user

    def refresh(self, refresh_token: str) -> tuple[str, str]:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise CredentialsError("Invalid refresh token")

        session = self.session_repo.get_by_refresh_hash(hash_token(refresh_token))
        if not session or session.is_revoked:
            raise CredentialsError("Session revoked or not found")

        self.session_repo.revoke(session)

        new_session_id = generate_jti()
        new_access = create_access_token(subject=payload["sub"], jti=new_session_id)
        new_refresh = create_refresh_token(subject=payload["sub"], jti=new_session_id)

        new_session = SessionModel(
            id=new_session_id,
            user_id=session.user_id,
            refresh_token_hash=hash_token(new_refresh),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        self.session_repo.create(new_session)

        return new_access, new_refresh

    def logout(self, refresh_token: str) -> None:
        session = self.session_repo.get_by_refresh_hash(hash_token(refresh_token))
        if session:
            self.session_repo.revoke(session)

    def logout_all(self, user_id: str) -> None:
        self.session_repo.revoke_all_for_user(user_id)
