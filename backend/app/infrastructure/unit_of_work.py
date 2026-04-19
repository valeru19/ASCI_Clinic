from sqlalchemy.orm import Session


class UnitOfWork:
    def __init__(self, session: Session) -> None:
        self.session = session

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc:
            self.session.rollback()
        else:
            self.session.commit()
            
