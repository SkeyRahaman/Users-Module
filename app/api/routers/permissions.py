from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionOut
from app.database.services.permission_service import PermissionService
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
