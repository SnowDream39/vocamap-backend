from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# 标签标记了活动的特征。有几类不同的标签。
# 类别标签：表示这个活动的主要内容（KTV、观影会、同人展、讲座等）。
# 艺术家标签：表示与这个活动相关的艺术家（虚拟歌手、创作者等）。


class TagTypeEnum(str, Enum):
    category = "category"
    artist = "artist"

class TagRead(BaseModel):
    id: int
    type: TagTypeEnum
    name: str

class ArtistCreate(BaseModel):
    name: str

class TagUpdate(BaseModel):
    type: Optional[TagTypeEnum]
    name: Optional[str]

class TagBatchCreate(BaseModel):
    tags: List[ArtistCreate]

