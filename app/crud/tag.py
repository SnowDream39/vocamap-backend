from sqlalchemy import insert, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import *
from app.schemas.tag import *

async def create_artist(
    tag: ArtistCreate, 
    session: AsyncSession
) -> int:
    stmt = select(Tag.id).where(Tag.name == tag.name)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise Exception("标签已存在")
    
    stmt = insert(Tag).values(
        name=tag.name,
        type=TagTypeEnum.artist
    ).returning(Tag.id)
    result = await session.execute(stmt)
    tag_id = result.scalar_one()
    await session.commit()

    return tag_id


async def popular_artist_tags(
    session: AsyncSession
):
    stmt = (
        select(Tag)
        .join(ActivityTag, Tag.id == ActivityTag.tag_id)
        .where(Tag.type == TagTypeEnum.artist)
        .group_by(Tag.id)
        .order_by(func.count(ActivityTag.activity_id).desc())
    )


    result = await session.execute(stmt)
    rows = result.scalars().all()


    return rows

async def get_all_category_tags(
    session: AsyncSession
):
    stmt = select(Tag).where(Tag.type == TagTypeEnum.category)
    result = await session.execute(stmt)
    rows = result.scalars().all()

    return rows

async def delete_tag(
    tag_id: int,
    session: AsyncSession
) -> None:

    stmt = select(Tag).where(Tag.id == tag_id)
    result = await session.execute(stmt)
    tag = result.scalar_one_or_none()
    if not tag:
        raise Exception("标签不存在")
    await session.delete(tag)
    
    
    