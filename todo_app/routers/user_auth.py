from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer

from todo_app import container

from ..schemas.user import CreateUser, UserToken
from ..services.user_auth import UserAuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
_user_service: UserAuthService = Depends(Provide[container.Container.user_service])


@router.post("/register", status_code=status.HTTP_200_OK)
@inject
async def create_user(
    username: str,
    first_name: str,
    last_name: str,
    password: str,
    user_service: UserAuthService = _user_service,
) -> None:
    await user_service.registration(username, first_name, last_name, password)


@router.post("/login/", response_model=UserToken)
@inject
async def user_login(username: str, password: str, user_service: UserAuthService = _user_service) -> UserToken:
    return await user_service.login(username, password)


@router.post("/token/refresh", response_model=UserToken)
@inject
async def refresh_token(
    token: str = Depends(oauth2_scheme),
    user_service: UserAuthService = _user_service,
) -> UserToken:
    return await user_service.refresh_token(token)


@router.post("/token/verify", response_model=UserToken)
@inject
async def verify_token(
    token: str = Depends(oauth2_scheme),
    user_service: UserAuthService = _user_service,
) -> CreateUser:
    return await user_service.verify_token(token)


@router.post("/logout", response_model=dict, status_code=status.HTTP_200_OK)
@inject
async def logout(
    token: str = Depends(oauth2_scheme),
    user_service: UserAuthService = _user_service,
) -> dict[str, str]:
    await user_service.logout(token)
