from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    hashed_password: str


class CreateTokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserPatchRequests(BaseModel):
    username: str | None = None
