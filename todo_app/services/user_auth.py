from datetime import datetime, timedelta, timezone

import jwt
import ulid
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from ..core.config import settings
from ..models.user import User
from ..repositories.user_auth import UserAuthRepository
from ..schemas.user import (
    CreateTokenResponse,
    UserPatchRequests,
)

SECRET_KEY = settings.jwt.secret_key
ALGORITHM = settings.jwt.algoritm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserAuthService:
    def __init__(self, pwd_context: CryptContext, user_repository: UserAuthRepository) -> None:
        self.pwd_context = pwd_context
        self.user_repository = user_repository

    def verify_password(self, plain_password: str, password: str) -> bool:
        return self.pwd_context.verify(plain_password, password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.user_repository.get_by_username(username=username)

        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:  # noqa: PLR6301
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=1))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def get_user_from_token(self, *, token: str) -> str:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")

        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user = self.user_repository.get_by_username(username=username)

        if not user:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user.id

    async def refresh_token(self, token: str) -> CreateTokenResponse:
        user = await self.verify_token(token)
        access_token = self.create_access_token(data={"sub": user.username})
        return CreateTokenResponse(
            access_token=access_token,
            token_type="bearer",  # noqa: S106
        )

    async def verify_token(self, token: str) -> User:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise {"message": "User not fount"}
        token_data = UserPatchRequests(username=username)

        return self.user_repository.get_by_username(username=token_data.username)

    async def registration(self, *, username: str, first_name: str, last_name: str, password: str) -> None:
        hashed_password = self.get_password_hash(password)
        new_user = User(
            id=str(ulid.ULID()),
            username=username,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
        )
        return self.user_repository.add_user(new_user)

    async def login(self, *, token: OAuth2PasswordRequestForm) -> CreateTokenResponse:
        user = self.authenticate_user(token.username, token.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires,
        )
        return CreateTokenResponse(access_token=access_token, token_type="bearer")  # noqa: S106
