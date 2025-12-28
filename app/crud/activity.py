
from fastapi import HTTPException
from app.models import Activity, User, Tag, ActivityParticipant, ActivityTag
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityTableCreate
from datetime import datetime
from sqlalchemy import text, select, delete, update, insert, exists, func, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.types import Geography
from geoalchemy2.shape import to_shape
from geoalchemy2 import functions as geo_func
from shapely.geometry import mapping

act_sel_columns = [
    Activity.id,
    Activity.name,
    Activity.description,
    Activity.location,
    Activity.start_time,
    Activity.end_time,
    Activity.max_member,
    Activity.position
]

tag_sel_columns = [
    Tag.id.label("tag_id"),
    Tag.name.label("tag_name"),
    Tag.type.label("tag_type"),
]

user_sel_columns = [
    User.id,
    User.nickname,
]

tags_agg = func.coalesce(
        func.jsonb_agg(
            func.jsonb_build_object(
                "id", Tag.id,
                "name",Tag.name,
                "type", Tag.type
            )
        ).filter(Tag.id.isnot(None)),
        text("'[]'::JSONB")
    ).label("tags")

owner_json = func.jsonb_build_object(
    "id", User.id,
    "nickname", User.nickname
).label("owner")

full_activity_select = [
    *act_sel_columns, 
    tags_agg,
    owner_json,
]
select_full_from_activity_stmt = (
    select(*full_activity_select)
    .select_from(Activity)
    .outerjoin(ActivityTag, ActivityTag.activity_id == Activity.id)
    .outerjoin(Tag, ActivityTag.tag_id == Tag.id)
    .outerjoin(User, User.id == Activity.owner_id)
    .group_by(*act_sel_columns, *user_sel_columns)
)

#  =========== 数据转换操作 ===========

def activity_map_to_json(rowMapping):
    row = dict(rowMapping)
    row["position"] = mapping(to_shape(rowMapping.position))
    return row



# =========== 查询 ===========

async def get_all_activities(
    session: AsyncSession
):
    result = await session.execute(select_full_from_activity_stmt)
    activities = result.mappings().all()
    return [activity_map_to_json(activity) for activity in activities]

async def get_activity_by_id(
    activity_id: int,
    session: AsyncSession
):
    stmt = (
        select_full_from_activity_stmt
        .where(Activity.id == activity_id)
    )
    result = await session.execute(stmt)
    activity = result.mappings().first()
    print(activity)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    return activity_map_to_json(activity)


async def activities_of_owner(
    user_id: int,
    session: AsyncSession
):
    stmt = (
        select_full_from_activity_stmt
        .where(Activity.owner_id == user_id)
    )
    
    result = await session.execute(stmt)
    activities = result.mappings().all()
    
    
    return [activity_map_to_json(activity) for activity in activities]

async def activities_of_participant(
    user_id: int,
    session: AsyncSession
):
    stmt = (
        select_full_from_activity_stmt
        .where(ActivityParticipant.user_id == user_id)
    )
    
    result = await session.execute(stmt)
    activities = result.mappings().all()
    
    return [activity_map_to_json(activity) for activity in activities]

async def activities_of_tag(
    tag_id: int,
    session: AsyncSession
):
    stmt = (
        select_full_from_activity_stmt
        .where(Tag.id == tag_id)
    )
    
    result = await session.execute(stmt)
    activities = result.mappings().all()
    print(activities)
    
    return [activity_map_to_json(activity) for activity in activities]

async def nearby_activities(
    lon: float,
    lat: float,
    distance: float,
    session: AsyncSession
):
    stmt = (
        select_full_from_activity_stmt
        .where(
            Activity.position.ST_DWithin(
                text("ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography"),
                distance,
                True
            )
        )
    )
    result = await session.execute(stmt, {"lon": lon, "lat": lat})
    activities = result.mappings().all()
    return [activity_map_to_json(activity) for activity in activities]

async def activities_by_time_point(
    given_time: datetime,
    session: AsyncSession
):
    stmt = (
        select_full_from_activity_stmt
        .where(
            Activity.start_time <= given_time,
            Activity.end_time >= given_time
        )
    )
    result = await session.execute(stmt)
    activities = result.mappings().all()
    return [activity_map_to_json(activity) for activity in activities]

async def activities_by_time_period(
    start_time: datetime,
    end_time: datetime,
    session: AsyncSession
):
    stmt = (
        select_full_from_activity_stmt
        .where(
            Activity.start_time <= end_time,
            Activity.end_time >= start_time
        )
    )
    result = await session.execute(stmt)
    activities = result.mappings().all()
    return [activity_map_to_json(activity) for activity in activities]


async def search_activities(
    keywords: list[str] | None,
    tag_ids: list[int] | None,
    max_member_gt: int | None,
    max_member_lt: int | None,
    time_begin: datetime | None,
    time_end: datetime | None,
    session: AsyncSession
):  
    where_clauses = []
    for keyword in keywords or []:
        where_clauses.append(
            Activity.name.contains(keyword)
        )
    for tag_id in tag_ids or []:
        where_clauses.append(
            ActivityTag.tag_id == tag_id
        )
    if max_member_gt:
        where_clauses.append(
            Activity.max_member >= max_member_gt
        )
    if max_member_lt:
        where_clauses.append(
            Activity.max_member <= max_member_lt
        )
    if time_begin:
        where_clauses.append(
            Activity.end_time >= time_begin
        )
    if time_end:
        where_clauses.append(
            Activity.start_time <= time_end
        )
    stmt = (
        select_full_from_activity_stmt
        .where(*where_clauses)
    )
    result = await session.execute(stmt)
    activities = result.mappings().all()
    return [activity_map_to_json(activity) for activity in activities]


# =========== 增删改  =================


async def create_activity(
    activity: ActivityCreate,
    user_id: int,
    session: AsyncSession
) -> int:

    data = ActivityTableCreate.model_validate(
        activity.model_dump(
            include={
                "name","start_time","end_time",
                "location","max_member","description"
            }
        )
    )

    activity_in_db = Activity(
        **data.model_dump(),
        position=geo_func.ST_MakePoint(
            activity.position.lon,
            activity.position.lat
        ).cast(Geography(srid=4326)),
        owner_id = user_id
    )
    session.add(activity_in_db)
    await session.commit()
    await session.refresh(activity_in_db)
    return activity_in_db.id

async def update_activity(
    activity_id: int,
    user_id: int,
    activityUpdate: ActivityUpdate,
    session: AsyncSession
):
    result = await session.execute(select(Activity).where(Activity.id == activity_id))
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    if activity.owner_id != user_id:
        raise HTTPException(status_code=403, detail="只有发起者才能修改活动")
    
    await session.execute(
        update(Activity)
        .where(Activity.id == activity_id)
        .values(**activityUpdate.model_dump())
    )
    await session.commit()
    

async def delete_activity(
    activity_id: int,
    session: AsyncSession
):
    result = await session.execute(select(Activity).where(Activity.id == activity_id))
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    await session.delete(activity)
    await session.commit()


async def user_join_activity(
    activity_id: int, 
    user_id: int,
    session: AsyncSession
):
    # 检查活动是否可加入
    stmt = select(Activity).where(Activity.id == activity_id)
    result = await session.execute(stmt)
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    stmt = select(
        exists().where(
            ActivityParticipant.activity_id == activity_id,
            ActivityParticipant.user_id == user_id
        )
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户已加入该活动")
    
    stmt = (
        select(func.count())
        .where(ActivityParticipant.activity_id == activity_id)
    )
    result = await session.execute(stmt)
    if activity.max_member <= result.scalar_one():
        raise HTTPException(status_code=400, detail="活动已满")
    stmt = (
        insert(ActivityParticipant)
        .values(
            activity_id=activity_id,
            user_id=user_id
        )
    )
    await session.execute(stmt)
    await session.commit()
    
async def user_leave_activity(
    activity_id: int, 
    user_id: int,
    session: AsyncSession
):
    result = await session.execute(select(Activity).where(Activity.id == activity_id))
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user not in activity.participants:
        raise HTTPException(status_code=400, detail="用户未加入该活动")
    await session.execute(
        delete(ActivityParticipant)
        .where(
            ActivityParticipant.activity_id == activity_id, 
            ActivityParticipant.user_id == user_id
            )
        )
    
async def add_tags_to_activity(
    activity_id: int, 
    tag_ids: list[int],
    session: AsyncSession
):
    for tag_id in tag_ids:
        await session.execute(
            insert(ActivityTag)
            .values(activity_id=activity_id, tag_id=tag_id)
            )
    
    await session.commit()