from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.session import Session as SessionModel


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session: SessionModel) -> SessionModel:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_refresh_hash(self, refresh_hash: str) -> SessionModel | None:
        return self.db.query(SessionModel).filter(SessionModel.refresh_token_hash == refresh_hash).first()

    def revoke(self, session: SessionModel) -> None:
        session.is_revoked = True
        session.revoked_at = datetime.now(timezone.utc)
        self.db.commit()

    def revoke_all_for_user(self, user_id: str) -> None:
        self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id, SessionModel.is_revoked == False
        ).update({"is_revoked": True, "revoked_at": datetime.now(timezone.utc)})
        self.db.commit()

    def delete_user_sessions(self, user_id: str) -> None:
        self.db.query(SessionModel).filter(SessionModel.user_id == user_id).delete()
        self.db.commit()