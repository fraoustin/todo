from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    token: str
    disabled: Optional[bool] = False
    isadmin: Optional[bool] = False
    onlyapi: Optional[bool] = False

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    disabled: Optional[bool] = False
    isadmin: Optional[bool] = False
    onlyapi: Optional[bool] = False
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    token: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None
    isadmin: Optional[bool] = None
    onlyapi: Optional[bool] = None

class UserUpdateMe(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None

class UserOut(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

#    class Config:
#        orm_mode = True