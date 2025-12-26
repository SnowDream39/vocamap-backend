from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional
from app.schemas.user import UserRead

# 活动是用户发布的，定位在地图上某个位置的活动。
# 主要属性：名称、开始时间、结束时间、位置、人数范围、主办者、参与者（用户）、简介、标签

class Position(BaseModel):
    lon: float
    lat: float

    def to_geojson(self):
        return {"type": "Point", "coordinates": [self.lon, self.lat]}
    
    def to_wkt(self):
        return f"POINT({self.lon} {self.lat})"

class ActivityRead(BaseModel):
    id: int
    name: str
    start_time: datetime
    end_time: datetime
    position: Position
    max_member: Optional[int] = None
    owner_id: int
    holder: Optional[UserRead] = None
    description: Optional[str] = None

    participant_ids: List[int] = Field(default_factory=list)
    tag_ids: List[int] = Field(default_factory=list)

    @field_validator("position", mode="before")
    def parse_geojson_position(cls, v):
        if isinstance(v, dict) and "coordinates" in v:
            lon, lat = v["coordinates"]
            return {"lon": lon, "lat": lat}
        return v
    

class ActivityTableCreate(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    max_member: Optional[int] = None
    description: Optional[str] = None
    location: Optional[str] = None




class ActivityCreate(ActivityTableCreate):
    position: Position
    tag_ids: List[int] = Field(default_factory=list)
    
    @field_validator("position", mode="before")
    def parse_geojson_position(cls, v):
        if isinstance(v, dict) and "coordinates" in v:
            lon, lat = v["coordinates"]
            return {"lon": lon, "lat": lat}
        return v

class ActivityUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    position: Optional[Position] = None
    max_member: Optional[int] = None
    description: Optional[str] = None

    @field_validator("position", mode="before")
    def parse_geojson_position(cls, v):
        if isinstance(v, dict) and "coordinates" in v:
            lon, lat = v["coordinates"]
            return {"lon": lon, "lat": lat}
        return v