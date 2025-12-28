from fastapi import APIRouter, HTTPException, Query, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.session import get_async_session
from app.schemas.tag import *
from app.models import User
from app.user_manager import current_active_user, current_super_user
from app.crud.tag import *


router = APIRouter(prefix="/tag", tags=["Tag"])

# 查询热门标签
@router.get("/popular")
async def get_popular_artists(
    session: AsyncSession = Depends(get_async_session)
):

    return await popular_artist_tags(session)

# 获取类别标签列表
@router.get("/category")
async def get_category_tags(
    session: AsyncSession = Depends(get_async_session)
):

    return await get_all_category_tags(session)

# 创建单个标签（仅允许artist标签）
@router.post("/create_artist")
async def create(
    tag: ArtistCreate = Body(...), 
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    ):

        tag_id = await create_artist(tag, session)    
        return {"success": True, "tag_id": tag_id}


# 删除标签，仅管理员
router.delete("/delete/{tag_id}")
async def delete(
    tag_id: int,
    user: User = Depends(current_super_user),
    session: AsyncSession = Depends(get_async_session)
    ):
   
    await delete_tag(tag_id, session)
    return {"success": True}