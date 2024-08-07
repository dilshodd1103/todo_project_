from sqlalchemy.orm import Mapped

from .base import AbstractBase


class Todo(AbstractBase):
    __tablename__ = "todo"

    title: Mapped[str]
    description: Mapped[str]
    done: Mapped[bool]
