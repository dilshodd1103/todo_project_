from ..core.database import Database
from ..models.user import User


class UserAuthRepository:
    def __init__(self, database: Database) -> None:
        self.database = database
        self.session_factory = self.database.session

    def get_by_username(self, username: str) -> User:
        with self.session_factory() as db:
            return db.query(User).filter(User.username == username).one()

    def add_user(self, new_user: User) -> None:
        with self.session_factory() as db:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
