from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
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
from ..services.user_auth import UserAuthService

router = APIRouter(prefix="/todos", tags=["todo"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_todo_service: services.TodoService = Depends(Provide[container.Container.todo_service])
_todo_repositories: repositories.TodoRepository = Depends(Provide[container.Container.todo_repository])
_user_service: UserAuthService = Depends(Provide[container.Container.user_service])


@router.get("/", response_model=list[GetTodoResponse])
@inject
def get_todos(todo_repository: repositories.TodoRepository = _todo_repositories) -> list[models.Todo]:
    return todo_repository.find_all()


@router.post(
    "/create",
    response_model=CreateTodoResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
def create_todo(
    data: CreateTodoRequest,
    token: Annotated[str, Header(validation_alias="Authorization")],
    todo_service: services.TodoService = _todo_service,
    user_service: UserAuthService = _user_service,
) -> models.Todo:
    owner_id = user_service.get_user_from_token(token=token)
    return todo_service.create(
        title=data.title,
        description=data.description,
        done=data.done,
        owner_id=owner_id,
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
