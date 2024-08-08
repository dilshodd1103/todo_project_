from pydantic import BaseModel, ConfigDict, Field


class CreateTodoRequest(BaseModel):
    title: str
    description: str
    done: bool


class CreateTodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str


class GetTodoResponse(BaseModel):
    id: str
    title: str
    description: str
    done: bool


class TodoPatchRequest(BaseModel):
    title: str = Field(None)
    description: str = Field(None)
    done: bool = Field(None)
