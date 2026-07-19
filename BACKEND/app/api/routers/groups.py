from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user, require_permission
from app.schemas import GroupCreate, GroupUpdate, GroupOut, AddUserToGroupForGroup, AddRoleToGroupForGroup, RoleOut, UserOut
from app.database.services import GroupService, UserGroupService, GroupRoleService

from app.database.models import User


router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

# 🔸 POST /groups/ - Create new group
@router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED, name="create_group")
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    group = await GroupService.create_group(db, group_data)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group name already exists"
        )
    return group


# 🔸 GET /groups/ - List all groups
@router.get("/", response_model=list[GroupOut], name="get_all_groups")
async def get_all_groups(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    return await GroupService.get_all_groups(
        db,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )


# 🔸 GET /groups/{id} - Get group by ID
@router.get("/{id}", response_model=GroupOut, name="get_group")
async def get_group(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    group = await GroupService.get_group_by_id(db, id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return group


# 🔸 PUT /groups/{id} - Update group
@router.put("/{id}", response_model=GroupOut, name="update_group")
async def update_group(
    id: int,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    group = await GroupService.update_group(db, id, group_data)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return group


# 🔸 DELETE /groups/{id} - Delete group (soft delete)
@router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED, name="delete_group")
async def delete_group(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    deleted = await GroupService.delete_group(db, id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return {"message": "Group deleted"}

# POST /groups/{id}/add_user - Add user to group
@router.post("/{group_id}/add_user", name="add_user_to_group", status_code=status.HTTP_201_CREATED, dependencies=[require_permission("assign_user_to_group")])
async def add_user_to_group(
    group_id: int,
    request_data: AddUserToGroupForGroup,
    db: AsyncSession = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    db_respons = await UserGroupService.assign_user_group(db=db, user_id=request_data.user_id, group_id=group_id, created_by=current_user.id)
    if not db_respons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add user to group. Check if user and group exist."
        )
    return {
        "message": "User added to group successfully",
        "group_id": group_id,
        "user_id": request_data.user_id,
        "timestamp": datetime.now()
        }

# POST /group/{id}/remove_user
@router.post("/{group_id}/remove_user", name="remove_user_from_group", status_code=status.HTTP_202_ACCEPTED, dependencies=[require_permission("remove_user_from_group")])
async def remove_user_from_group(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    db_response = await UserGroupService.remove_user_group(db=db, group_id=group_id, user_id=user_id)
    if not db_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove user from group. Check if user and group exist or if the user was part of the group."
        )
    return {"message": "User removed from group successfully"}

# Get /groups/{group_id}/users - Get users of a group
@router.get("/{group_id}/users", name="get_users_of_group", response_model=list[UserOut], status_code=status.HTTP_200_OK, dependencies=[require_permission("remove_user_from_group")])
async def get_users_of_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    users = await UserGroupService.get_all_users_for_group(db=db, group_id=group_id)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found or no users assigned"
        )
    return users

# POST /groups/{group_id}/assigne_role 
@router.post("/{group_id}/assigne_role", name="assign_role_to_group", status_code=status.HTTP_201_CREATED, dependencies=[require_permission("remove_user_from_group")])
async def assign_role_to_group(
    group_id: int,
    request_data: AddRoleToGroupForGroup,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_response = await GroupRoleService.assign_group_role(
        db=db,
        group_id=group_id,
        role_id=request_data.role_id,
        valid_from= request_data.valid_from,
        valid_until= request_data.valid_until,
        created_by=current_user.id
    )
    if not db_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign role to group. Check if role and group exist."
        )
    return {
        "message": "Role assigned to group successfully",
        "group_id": group_id,
        "role_id": request_data.role_id,
        "timestamp": datetime.now()
        }
    
# POST /groups/{group_id}/remove_role   
@router.post("/{group_id}/remove_role", name="remove_role_from_group", status_code=status.HTTP_202_ACCEPTED, dependencies=[require_permission("remove_user_from_group")])
async def remove_role_from_group(
    group_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    db_response = await GroupRoleService.remove_group_role(db=db, group_id=group_id, role_id=role_id)
    if not db_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove role from group. Check if role and group exist or if the role was assigned to the group."
        )
    return {"message": "Role removed from group successfully"}

# GET /groups/{group_id}/roles - Get roles of a group
@router.get("/{group_id}/roles", name="get_roles_of_group", response_model=list[RoleOut], status_code=status.HTTP_200_OK, dependencies=[require_permission("remove_user_from_group")])
async def get_roles_of_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    roles = await GroupRoleService.get_all_roles_for_group(db=db, group_id=group_id)
    if roles is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found or no roles assigned"
        )
    return roles

# 🔸 GET /groups/name/{name} - Get group by name
@router.get("/name/{name}", response_model=GroupOut, name="get_group_by_name")
async def get_group_by_name(
    name: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    group = await GroupService.get_group_by_name(db, name)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return group
