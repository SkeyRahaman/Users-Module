from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.schemas.group import GroupCreate, GroupUpdate, GroupOut
from app.database.services.group_service import GroupService
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


# 🔸 GET /groups/name/{name} - Get group by name
@router.get("/name/{name}", response_model=GroupOut, name="get_group_by_name")
async def get_group_by_name(
    name: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    group = await GroupService.get_group_by_name(db, name)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return group
