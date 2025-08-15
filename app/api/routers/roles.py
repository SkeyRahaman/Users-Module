from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut
from app.database.services.role_service import RoleService
from app.database.models import User


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
