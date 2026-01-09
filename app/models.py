from typing import Optional, List
from sqlmodel import SQLModel, Field, JSON, Column
from datetime import datetime

class Camera(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    location: Optional[str] = None
    rtsp_url: str
    status: str = "offline"
    fps: Optional[float] = None
    last_frame_time: Optional[datetime] = None
    zones: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    camera_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    rule: str
    object_type: Optional[str] = None
    confidence: Optional[float] = None
    bbox: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    snapshot_path: Optional[str] = None
