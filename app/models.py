import enum
from datetime import datetime
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import ForeignKey, String, Integer, Text, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM
from geoalchemy2 import Geography
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2.elements import WKBElement

Base = declarative_base()

# =====================
# 枚举类型
# =====================
class TagTypeEnum(enum.Enum):
    category = "category"
    artist = "artist"

class GenderEnum(enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class UserTypeEnum(enum.Enum):
    admin = "admin"
    normal = "normal"

# =====================
# tags 表
# =====================
class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    type: Mapped[TagTypeEnum] = mapped_column(
        ENUM(TagTypeEnum, name="tag_type_enum", create_type=True),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 反向关系
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_tags",
        back_populates="tags"
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        secondary="activity_tags",
        back_populates="tags"
    )

# =====================
# users 表
# =====================
class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False, default="新用户")
    gender: Mapped[GenderEnum] = mapped_column(
        ENUM(GenderEnum, name="gender_enum", create_type=True),
        nullable=False,
        default=GenderEnum.other
    )
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    signup_time: Mapped[datetime] = mapped_column(DateTime(True), nullable=False, default=datetime.now)

    # 反向关系
    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        secondary="user_tags",
        back_populates="users"
    )
    own_activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="owner")
    joined_activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        secondary="activity_participants",
        back_populates="participants"
    )

# =====================
# user_tags 表 (关联表)
# =====================
class UserTag(Base):
    __tablename__ = "user_tags"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True, index=True)

# =====================
# activities 表
# =====================
class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(True), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=True) 
    description: Mapped[str] = mapped_column(Text, nullable=True)
    max_member: Mapped[int] = mapped_column(Integer, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    position: Mapped[WKBElement] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=True)

    # 反向关系
    owner: Mapped["User"] = relationship("User", back_populates="own_activities")
    participants: Mapped[list["User"]] = relationship(
        "User",
        secondary="activity_participants",
        back_populates="joined_activities"
    )
    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        secondary="activity_tags",
        back_populates="activities"
    )

# =====================
# activity_participants 表 (关联表)
# =====================
class ActivityParticipant(Base):
    __tablename__ = "activity_participants"
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True,index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)

# =====================
# activity_tags 表 (关联表)
# =====================
class ActivityTag(Base):
    __tablename__ = "activity_tags"
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True, index=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True, index=True)
