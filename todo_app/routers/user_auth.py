from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from h11 import Response

from todo_app import container

from ..repositories.user_auth import UserAuthRepository
from ..schemas.user import CreateTokenResponse
from ..services.user_auth import UserAuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_user_service: UserAuthService = Depends(Provide[container.Container.user_service])
_user_repository: UserAuthRepository = Depends(Provide[container.Container.user_repository])


@router.post("/register", status_code=status.HTTP_200_OK)
@inject
async def register(
    username: str,
    first_name: str,
    last_name: str,
    password: str,
    user_service: UserAuthService = _user_service,
) -> None:
    await user_service.registration(username=username, first_name=first_name, last_name=last_name, password=password)


@router.post("/login")
@inject
async def user_login(
    token: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserAuthService = _user_service,
) -> CreateTokenResponse:
    return await user_service.login(token=token)


@router.post("/token/refresh")
@inject
async def refresh_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserAuthService = _user_service,
) -> CreateTokenResponse:
    try:
        return await user_service.refresh_token(token)
    except HTTPException:
        await Response(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


@router.post("/token/verify")
@inject
async def verify_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserAuthService = _user_service,
) -> None:
    try:
        await user_service.verify_token(token)
    except HTTPException:
        await Response(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
