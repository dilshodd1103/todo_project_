from typing import Any

from ulid import ULID

from ..models.todo import Todo
from ..repositories import TodoRepository


class TodoService:
    def __init__(self, todo_repository: TodoRepository) -> None:
        self.todo_repository = todo_repository

    def create(self, *, title: str, description: str, done: bool) -> Todo:
        instance = Todo(id=str(ULID()), title=title, description=description, done=done)
        return self.todo_repository.store(instance)

    def update(self, *, todo_id: str, **kwargs: Any) -> None:
        instance = self.todo_repository.get(todo_id)

        for key, value in kwargs.items():
            setattr(instance, key, value)

        self.todo_repository.store(instance)
