from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from fastapi_users import schemas

# 用户是APP的用户，有管理员和普通用户两种，不包括未注册用户
# 主要属性：昵称、性别、年龄、类别、注册日期、关注标签

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class UserType(str, Enum):
    admin = "admin"
    normal = "normal"

class UserRead(schemas.BaseUser[int]):
    nickname: str
    gender: Gender
    age: Optional[int] = None
    type: Optional[UserType] = None
    signup_time: datetime
    tag_ids: List[int] = Field(default_factory=list)

# 客户端提交明文密码（后端负责哈希）
class UserCreate(schemas.BaseUserCreate):
    nickname: str = Field(..., min_length=2, max_length=50)


class UserLogin(BaseModel):
    id: int
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    nickname: Optional[str] = Field(None, min_length=2, max_length=50)
    gender: Optional[Gender] = None
    age: Optional[int] = None
    tag_ids: Optional[List[int]] = None

    @field_validator("age")
    def age_nonnegative(cls, v):
        if v is not None and v < 0:
            raise ValueError("age must be non-negative")
        return v

