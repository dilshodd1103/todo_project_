from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from starlette import status

from .. import container, models, repositories, services
from ..models.todo import Todo
from ..schemas.todo import (
    CreateTodoRequest,
    CreateTodoResponse,
    GetTodoResponse,
    TodoPatchRequest,
)

router = APIRouter(prefix="/todos", tags=["todo"])

_todo_service: services.TodoService = Depends(Provide[container.Container.todo_service])
_todo_repositories: repositories.TodoRepository = Depends(Provide[container.Container.todo_repository])


@router.get("/", response_model=list[GetTodoResponse])
@inject
def get_todos(todo_repository: repositories.TodoRepository = _todo_repositories) -> list[models.Todo]:
    return todo_repository.find_all()


@router.post(
    "/",
    response_model=CreateTodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a todo",
)
@inject
def create_todo(
    data: CreateTodoRequest,
    todo_service: services.TodoService = _todo_service,
) -> models.Todo:
    return todo_service.create(
        title=data.title,
        description=data.description,
        done=data.done,
    )


@router.get("/{todo_id}", response_model=GetTodoResponse)
@inject
def get_todo(
    todo_id: str,
    todo_repository: repositories.TodoRepository = _todo_repositories,
) -> Todo:
    try:
        todos = todo_repository.get(todo_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    return todos


@router.patch("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def patch_todo(
    todo_id: str,
    data: TodoPatchRequest,
    todo_service: services.TodoService = _todo_service,
) -> None:
    todo_service.update(todo_id=todo_id, **data.model_dump(exclude_unset=True))


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_todo(
    todo_id: str,
    todo_repository: repositories.TodoRepository = _todo_repositories,
) -> None:
    try:
        todo_repository.delete(todo_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
