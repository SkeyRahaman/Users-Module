from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class PermissionOut(PermissionBase):
    id: int
    created: datetime
    updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
