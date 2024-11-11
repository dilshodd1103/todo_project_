from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from h11 import Response

from todo_app import container

from ..schemas.user import CreateTokenResponse, LoginRequest, CreateUserRequest
from ..services.user_auth import UserAuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_user_service: UserAuthService = Depends(Provide[container.Container.user_service])


@router.post("/register", status_code=status.HTTP_200_OK)
@inject
async def register(
    requests: CreateUserRequest,
    user_service: UserAuthService = _user_service,
) -> None:
    await user_service.registration(username=requests.username, first_name=requests.first_name, last_name=requests.last_name, password=requests.hashed_password)
    

@router.post("/login")
@inject
async def user_login(
    token: Annotated[str, Depends(OAuth2PasswordRequestForm)],
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
