import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError, PyJWTError
from passlib.context import CryptContext

from ..schemas.user import CreateUser, UserPassword, UserPatchRequests, UserToken
from .todo import TodoService

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

blacklist = set()

fake_users_db = {
    "dilshod": {
        "username": "dilshod",
        "first_name": "dilshodtech",
        "last_name": "Qurbonmurotov Dilshod",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    },
}


class UserAuthService:
    def __init__(self, todo_service: TodoService, pwd_context: CryptContext) -> None:
        self.todo_service = todo_service
        self.pwd_context = pwd_context

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, hashed_password: str) -> str:
        return self.pwd_context.hash(hashed_password)

    def get_user(self, db: dict[str, dict[str, str]], username: str) -> UserPassword | None:
        if username in db:
            user_dict = db[username]
            return CreateUser(**user_dict)
        return None

    def authenticate_user(self, username: str, password: str) -> CreateUser | None:
        user = self.get_user(fake_users_db, username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def refresh_token(self, token: str) -> UserToken:
        user = await self.verify_token(token)
        return await self.login(user["username"], user["hashed_password"])

    async def verify_token(self, token: str) -> CreateUser:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
        except InvalidTokenError:
            return credentials_exception
        user = self.get_user(fake_users_db, username=username)
        if user is None:
            return credentials_exception
        return user

    async def get_current_user(self, token: str) -> CreateUser:
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to recover credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            token_data = UserPatchRequests(username=username)
        except PyJWTError:
            return credential_exception
        user = self.get_user(fake_users_db, token_data.username)
        if user is None:
            return credential_exception
        return user

    async def registration(self, username: str, first_name: str, last_name: str, password: str) -> None:
        hashed_password = self.get_password_hash(password)
        user = CreateUser(
            username=username,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
        )
        fake_users_db[username] = user.dict()

    async def login(self, username: str, password: str) -> UserToken:
        user = self.authenticate_user(username, password)

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
        return UserToken(access_token=access_token, token_type=["bearer"])

    async def logout(self, token: str) -> None:
        blacklist.add(token)
