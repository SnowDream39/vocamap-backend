from fastapi import APIRouter, Query, Depends, Body
from typing import List
from app.schemas.activity import ActivityCreate, ActivityRead, ActivityUpdate
from datetime import datetime, timezone, timedelta
from app.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.activity import *
from app.user_manager import current_super_user, current_active_user

router = APIRouter(prefix="/activity", tags=["Activity"])

@router.get("/all")
async def get_all(
    session: AsyncSession = Depends(get_async_session)
    ):
    return await get_all_activities(session)


@router.get("/id/{activity_id}")
async def get_activity(
    activity_id: int,
    session: AsyncSession = Depends(get_async_session)
    ):
    return await get_activity_by_id(activity_id, session)

# 指定user_id，查询该user参加的所有活动
@router.get("/by_owner")
async def get_activities_by_holder(
    user_id: int = Query(...),
    session: AsyncSession = Depends(get_async_session)
    ):
    
    return await activities_of_owner(user_id, session)


# 指定user_id，查询该user参加的所有活动
@router.get("/by_participant")
async def get_activities_by_participant(
    user_id: int = Query(...),
    session: AsyncSession = Depends(get_async_session)
):
    return await activities_of_participant(user_id, session)


# 指定地点（lon,lat），查询该地点周围distance距离内的所有活动

@router.get("/nearby")
async def get_nearby_activities(
    lon: float = Query(...),
    lat: float = Query(...),
    distance: float = Query(..., description="单位：米"),
    session: AsyncSession = Depends(get_async_session)
):

    return await nearby_activities(lon, lat, distance, session)


# 指定时间点，查询该时间点正在进行的活动
@router.get("/time_point")
async def get_activities_by_time_point(
    given_time: datetime = Query(..., description="格式示例：2025-12-04T15:30:00"),
    session: AsyncSession = Depends(get_async_session)
):

    return await activities_by_time_point(given_time, session)

# 以(start_time,end_time)的形式指定时间段，查询与该时间段重叠的活动
@router.get("/time_period")
async def get_activities_by_time_period(
    start_time: datetime = Query(..., description="时间段开始"),
    end_time: datetime = Query(..., description="时间段结束"),
    session: AsyncSession = Depends(get_async_session)
):

    return await activities_by_time_period(start_time, end_time, session)


# 根据标签查询活动
@router.get("/by_tag")
async def get_activities_by_tag(
    tag_id: int = Query(..., description="指定标签ID"),
    session: AsyncSession = Depends(get_async_session)
):
    return await activities_of_tag(tag_id, session)

@router.get("/search")
async def activity_search(
    keywords: str = Query(None, description="多个关键词用空格隔开"),
    tag_ids: List[int] = Query(None),
    max_member_gt: int = Query(None, description="容纳人数下限"),
    max_member_lt: int = Query(None, description="容纳人数上限"),
    time_begin: datetime = Query(datetime(2025,12,27, tzinfo=timezone(timedelta(hours=8))), description="时间段开始"),
    time_end: datetime = Query(None, description="时间段结束"),
    session: AsyncSession = Depends(get_async_session)
):
    return await search_activities(keywords.split(), tag_ids, max_member_gt, max_member_lt, time_begin, time_end, session)

# 用户创建活动
@router.post("/create")
async def activity_create(
    activity: ActivityCreate = Body(..., description="活动信息"),
    session: AsyncSession = Depends(get_async_session),
    user = Depends(current_active_user),
    ):
    print(user.id)
    
    activity_id = await create_activity(activity, user.id, session)
    await user_join_activity(activity_id, user.id, session)
    await add_tags_to_activity(activity_id, activity.tag_ids, session)

    return {"success": True, "activity_id": activity_id}




# 用户修改活动
# 可以修改任意字段，owner_id除外。只有holder才能修改活动
# 对于position字段，传入Position(lon, lat)或者传入GeoJSON都是可以的
# 前端路由为 PUT "/api/activity/update/{activity_id}?user_id={user_id}" + json
@router.put("/update/{activity_id}")
async def activity_update(
    activity_id: int, 
    user_id: int, 
    activity: ActivityUpdate,
    session: AsyncSession = Depends(get_async_session)
    ):
    return await update_activity(activity_id, user_id, activity, session)

# 删除活动，只有superuser可以
# 前端路由为 DELETE "/api/activity/delete/{activity_id}"
@router.delete("/delete/{activity_id}")
async def activity_delete(
    activity_id: int, 
    session: AsyncSession = Depends(get_async_session),
    user = Depends(current_super_user),
    ):
    return await delete_activity(activity_id, session)


# 用户报名活动
@router.post("/join/{activity_id}")
async def join_activity(
    activity_id: int, 
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    ):
    
    return await user_join_activity(activity_id, user.id, session)


# 用户退出活动
@router.post("/leave/{activity_id}")
async def leave_activity(
    activity_id: int, 
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
    ):
    
    return await user_leave_activity(activity_id, user.id, session)