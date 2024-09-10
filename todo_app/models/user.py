from sqlalchemy.orm import Mapped, mapped_column

from .base import AbstractBase


class User(AbstractBase):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    hashed_password: Mapped[str]
