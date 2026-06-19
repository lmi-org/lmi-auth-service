from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.token_service import TokenService
from app.models.user import User

security = HTTPBearer(auto_error=False)


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_session_repo(db: Session = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
) -> AuthService:
    return AuthService(user_repo, session_repo)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
) -> UserService:
    return UserService(user_repo, session_repo)


def get_token_service(user_repo: UserRepository = Depends(get_user_repo)) -> TokenService:
    return TokenService(user_repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    token_service: TokenService = Depends(get_token_service),
) -> User:
    if not credentials:
        from app.core.exceptions import CredentialsError
        raise CredentialsError("Not authenticated")
    return token_service.get_current_user(credentials.credentials)
