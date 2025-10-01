from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user, require_permission
from app.schemas import PermissionCreate, PermissionUpdate, PermissionOut, AddPermissionToRoleForPermission
from app.database.services import PermissionService, RolePermissionService
from app.database.models import User

router = APIRouter(
    prefix="/permissions", 
    tags=["Permissions"]
)


# 🔸 POST /permissions/ - Create new permission
@router.post("/", response_model=PermissionOut, status_code=status.HTTP_201_CREATED, name="create_permission")
async def create_permission(
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    permission = await PermissionService.create_permission(db, permission_data)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission name already exists"
        )
    return permission


# 🔸 GET /permissions/ - List all permissions
@router.get("/", response_model=list[PermissionOut], name="get_all_permissions")
async def get_all_permissions(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    return await PermissionService.get_all_permissions(
        db,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )


# 🔸 GET /permissions/{id} - Get permission by ID
@router.get("/{id}", response_model=PermissionOut, name="get_permission")
async def get_permission(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    permission = await PermissionService.get_permission_by_id(db, id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission


# 🔸 PUT /permissions/{id} - Update permission
@router.put("/{id}", response_model=PermissionOut, name="update_permission")
async def update_permission(
    id: int,
    permission_data: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    permission = await PermissionService.update_permission(db, id, permission_data)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission


# 🔸 DELETE /permissions/{id} - Delete permission (soft delete)
@router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED, name="delete_permission")
async def delete_permission(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    deleted = await PermissionService.delete_permission(db, id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return {"message": "Permission deleted"}

# POST /permissions/{permission_id}/assigne_roles - Add permission to role
@router.post("/{permission_id}/assigne_roles", status_code=status.HTTP_201_CREATED, name="add_permission_to_role", dependencies=[require_permission("assign_role_to_user")])
async def add_permission_to_role(
    permission_id: int,
    request_data: AddPermissionToRoleForPermission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    added = await RolePermissionService.assign_role_permission(
        db=db,
        permission_id=permission_id,
        role_id=request_data.role_id,
        created_by=current_user.id
    )
    if not added:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add permission to role"
        )
    return {"message": "Permission added to role"}

# POST /permissions/{permission_id}/remove_roles - Remove permission from role
@router.post("/{permission_id}/remove_roles", status_code=status.HTTP_200_OK, name="remove_permission_from_role", dependencies=[require_permission("assign_role_to_user")])
async def remove_permission_from_role(
    permission_id: int,
    role_id: int,
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

# POST /permissions/{permission_id}/roles - List roles for a permission