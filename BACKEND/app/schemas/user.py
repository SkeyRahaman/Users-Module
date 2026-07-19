from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ✅ Base schema shared across Create, Update, Read
class UserBase(BaseModel):
    firstname: str = Field(..., max_length=50)
    middlename: Optional[str] = Field(default=None, max_length=50)
    lastname: str = Field(..., max_length=50)
    username: str = Field(..., max_length=30)
    email: EmailStr


# ✅ Schema for creating a new user (includes password)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


# ✅ Schema for updating an existing user (optional fields)
class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")  # optional but recommended

    firstname: Optional[str] = Field(default=None, max_length=50)
    middlename: Optional[str] = Field(default=None, max_length=50)
    lastname: Optional[str] = Field(default=None, max_length=50)
    username: Optional[str] = Field(default=None, max_length=30)
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    is_verified: Optional[bool] = Field(default=None)
    is_deleted: Optional[bool] = Field(default=None)


# ✅ Output schema for reading a user (includes DB-generated fields)
class UserOut(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_deleted: bool
    created: datetime
    updated: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)  # replaces orm_mode


# ✅ Output schema for full user with relations (optional)
class UserDetail(UserOut):
    roles: List[str] = []
    groups: List[str] = []

class UsersResponse(BaseModel):
    page: int
    limit: int
    total: int
    users: List[UserOut]
