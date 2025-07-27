from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleOut(RoleBase):
    id: int
    created: datetime
    updated: Optional[datetime] = None
    is_deleted: Optional[bool] = None  # Optional since it might not always be exposed

    model_config = ConfigDict(from_attributes=True)
    