from fastapi import APIRouter, HTTPException, Query, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.session import get_async_session
from app.schemas.tag import TagCreate, TagRead, TagBatchCreate
from app.models import User, Tag
from app.user_manager import current_super_user
from app.crud.tag import *
from typing import List


router = APIRouter(prefix="/tag", tags=["Tag"])

# 查询热门标签
# 前端路由形式为 GET '/api/tag/famous'
@router.get("/popular")
async def get_popular_tags(
    session: AsyncSession = Depends(get_async_session)
):

    return await popular_tags(session)

# 创建单个标签，仅管理员
# 前端路由形式为 POST '/api/tag/create?user_id={user_id}' json
@router.post("/create")
async def create(
    tag: TagCreate = Body(...), 
    user: User = Depends(current_super_user),
    session: AsyncSession = Depends(get_async_session),
    ):

        tag_id = await create_tag(tag, session)    
        return {"success": True, "tag_id": tag_id}


# 删除标签，仅管理员
# 前端路由形式为 DELETE '/api/tag/delete_tag/{tag_id}?user_id={user_id}'
router.delete("/delete/{tag_id}")
async def delete(
    tag_id: int, user_id: int = Query(...),
    user: User = Depends(current_super_user),
    session: AsyncSession = Depends(get_async_session)
    ):
   
    await delete_tag(tag_id, session)
    return {"success": True}