from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class GroupOut(GroupBase):
    id: int
    created: datetime
    updated: Optional[datetime] = None
    is_deleted: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)
    