from sqlalchemy import column
from sqlalchemy.orm import Mapped, mapped_column

from .base import AbstractBase


class Todo(AbstractBase):
    __tablename__ = "todo"

    title: Mapped[str]
    description: Mapped[str]
    done: Mapped[bool]
