import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.models.user import User


class SQLAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: str) -> User | None:
        parsed_user_id = uuid.UUID(user_id)
        stmt = select(User).where(User.id == parsed_user_id)
        return self.session.execute(stmt).scalar_one_or_none()
