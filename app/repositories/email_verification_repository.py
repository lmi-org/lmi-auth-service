from sqlalchemy.orm import Session

from app.models.email_verification import EmailVerification


class EmailVerificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, verification: EmailVerification) -> EmailVerification:
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        return verification

    def get_by_token_hash(self, token_hash: str) -> EmailVerification | None:
        return (
            self.db.query(EmailVerification)
            .filter(EmailVerification.token_hash == token_hash)
            .first()
        )
