from pydantic import BaseModel, ConfigDict
from typing import Optional

class TodoBase(BaseModel):
    text: str
    terminated: Optional[bool] = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    text: Optional[str] = None
    terminated: Optional[bool] = None

class TodoOut(TodoBase):
    id: int
    who: int

    model_config = ConfigDict(from_attributes=True)