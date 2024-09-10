from sqlalchemy import schema
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import AbstractBase
from .user import User


class Todo(AbstractBase):
    __tablename__ = "todos"

    title: Mapped[str]
    description: Mapped[str]
    done: Mapped[bool]

    owner_id: Mapped[str] = mapped_column(schema.ForeignKey(User.id))
    owner: Mapped[User] = relationship()
