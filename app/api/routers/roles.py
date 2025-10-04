from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user, require_permission
from app.schemas import RoleCreate, RoleUpdate, RoleOut, AddRoleToUserForRole, AddRoleToGroupForRole, AddPermissionToRoleForRole, PermissionOut, UserOut, GroupOut
from app.database.services import RoleService, UserRoleService, GroupRoleService, RolePermissionService
from app.database.models import User
from app.utils.logger import log


router = APIRouter(
    prefix="/roles", 
    tags=["Roles"]
)

# 🔸 POST /roles/ - Create new role
@router.post("/", response_model=RoleOut, status_code=status.HTTP_201_CREATED, name="create_role")
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    role = await RoleService.create_role(db, role_data)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )
    return role


# 🔸 GET /roles/ - List all roles
@router.get("/", response_model=list[RoleOut], name="get_all_roles")
async def get_all_roles(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    return await RoleService.get_all_roles(
        db,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )


# 🔸 GET /roles/{id} - Get role by ID
@router.get("/{id}", response_model=RoleOut, name="get_role")
async def get_role(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    role = await RoleService.get_role_by_id(db, id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


# 🔸 PUT /roles/{id} - Update role
@router.put("/{id}", response_model=RoleOut, name="update_role")
async def update_role(
    id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    role = await RoleService.update_role(db, id, role_data)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


# 🔸 DELETE /roles/{id} - Delete role (soft delete)
@router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED, name="delete_role")
async def delete_role(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    deleted = await RoleService.delete_role(db, id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return {"message": "Role deleted"}

# POST /roles/{role_id}/assign_user/ - Assign role to user
@router.post("/{role_id}/assign_user", status_code=status.HTTP_201_CREATED, name="assign_role_to_user", dependencies=[require_permission("assign_role_to_user")])
async def assign_role_to_user(
    role_id: int,
    request_data: AddRoleToUserForRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assigned = await UserRoleService.assigne_user_role(
        db=db,
        user_id=request_data.user_id,
        role_id=role_id,
        valid_from= request_data.valid_from,
        valid_until= request_data.valid_until,
        created_by=current_user.id
    )
    if not assigned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign role to user"
        )
    return {"message": "Role assigned to user"}

# POST /roles/{role_id}/remove_user/ - Remove role from user
@router.post("/{role_id}/remove_user", status_code=status.HTTP_202_ACCEPTED, name="remove_role_from_user", dependencies=[require_permission("assign_role_to_user")])
async def remove_role_from_user(
    role_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    removed = await UserRoleService.remove_user_role(
        db=db,
        user_id=user_id,
        role_id=role_id
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove role from user"
        )
    return {"message": "Role removed from user"}

#GET /roles/{role_id}/users - Get all users for a role
@router.get("/{role_id}/users", response_model=list[UserOut], name="get_users_for_role", dependencies=[require_permission("view_roles")])
async def get_users_for_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    users = await UserRoleService.get_all_users_for_role(db, role_id)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return users

# POST /roles/{role_id}/assigne_group/ - Assign role to group
@router.post("/{role_id}/assign_group", status_code=status.HTTP_201_CREATED, name="assign_role_to_group", dependencies=[require_permission("assign_role_to_user")])
async def assign_role_to_group(
    role_id: int,
    request_data: AddRoleToGroupForRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assigned = await GroupRoleService.assign_group_role(
        db=db,
        group_id=request_data.group_id, 
        role_id=role_id,
        valid_from= request_data.valid_from,
        valid_until= request_data.valid_until,
        created_by=current_user.id
    )
    if not assigned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign role to group"
        )
    return {"message": "Role assigned to group"}   

# POST /roles/{role_id}/remove_group/ - Remove role from group
@router.post("/{role_id}/remove_group", status_code=status.HTTP_202_ACCEPTED, name="remove_role_from_group", dependencies=[require_permission("assign_role_to_user")])
async def remove_role_from_group(
    role_id: int,
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    removed = await GroupRoleService.remove_group_role(
        db=db,
        group_id=group_id,
        role_id=role_id
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove role from group"
        )
    return {"message": "Role removed from group"} 

# GET /roles/{role_id}/groups - Get all groups for a role
@router.get("/{role_id}/groups", response_model=list[GroupOut], name="get_groups_for_role", dependencies=[require_permission("view_roles")])
async def get_groups_for_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    groups = await GroupRoleService.get_all_groups_for_role(db, role_id)
    if groups is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return groups

# POST /roles/{role_id}/add_permission/ - Add permission to role
@router.post("/{role_id}/assigne_permission", status_code=status.HTTP_201_CREATED, name="add_permission_to_role", dependencies=[require_permission("assign_role_to_user")])
async def add_permission_to_role(
    role_id: int,
    request_data: AddPermissionToRoleForRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    added = await RolePermissionService.assign_role_permission(
        db=db,
        permission_id=request_data.permission_id,
        role_id=role_id,
        created_by=current_user.id
    )
    if not added:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add permission to role"
        )
    return {"message": "Permission added to role"}

# POST /roles/{role_id}/remove_permission/ - Remove permission from role
@router.post("/{role_id}/remove_permission", status_code=status.HTTP_202_ACCEPTED, name="remove_permission_from_role", dependencies=[require_permission("assign_role_to_user")])
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    removed = await RolePermissionService.remove_role_permission(
        db=db,
        permission_id=permission_id,
        role_id=role_id
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove permission from role"
        )
    return {"message": "Permission removed from role"}

# GET /roles/{role_id}/permissions - Get all permissions for a role
@router.get("/{role_id}/permissions", response_model=list[PermissionOut], name="get_permissions_for_role", dependencies=[require_permission("view_roles")])
async def get_permissions_for_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    permissions = await RolePermissionService.get_all_permissions_for_role(db, role_id)
    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return permissions
