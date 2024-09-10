from pydantic import BaseModel, ConfigDict


class CreateUser(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    hashed_password: str


class UserPassword(CreateUser):
    pass


class UserConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserToken(BaseModel):
    access_token: str
    token_type: list[str]


class UserPatchRequests(BaseModel):
    username: str | None = None
