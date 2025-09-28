from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ValiditySchema(BaseModel):
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

class AddUserToGroupForGroup(ValiditySchema):
    user_id: int

class AddUserToGroupForUser(ValiditySchema):
    group_id: int
