from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from .permission import PermissionOut
from .user import UserOut
from .group import GroupOut
from .role import RoleOut


class ValiditySchema(BaseModel):
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

class AddUserToGroupForGroup(ValiditySchema):
    user_id: int

class AddUserToGroupForUser(ValiditySchema):
    group_id: int

class AddRoleToUserForUser(ValiditySchema):
    role_id: int

class AddRoleToUserForRole(ValiditySchema):
    user_id: int

class AddRoleToGroupForGroup(ValiditySchema):
    role_id: int

class AddRoleToGroupForRole(ValiditySchema):
    group_id: int

class AddPermissionToRoleForRole(ValiditySchema):
    permission_id: int

class AddPermissionToRoleForPermission(ValiditySchema):
    role_id: int
    
class RolesWithPermissions(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: list[PermissionOut] = []

    class Config:
        orm_mode = True

class PermissionsWithRoles(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    roles: list[RoleOut] = []

    class Config:
        orm_mode = True
