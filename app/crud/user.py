from fastapi import HTTPException
from sqlalchemy import select, update, insert, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
import json
from app.schemas.user import UserCreate, UserLogin, UserRead, UserUpdate, Gender, UserType
from app.models import User, GenderEnum, UserTypeEnum, UserTag

    
async def add_tags_to_user(
    user_id: int, 
    tag_ids: List[int],
    session: AsyncSession
):
    for tag_id in tag_ids:
        await session.execute(
            insert(UserTag)
            .values(user_id=user_id, tag_id=tag_id)
            )
    
    await session.commit() 
    