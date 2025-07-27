from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.schemas.group import GroupCreate, GroupUpdate, GroupOut
from app.services.group_service import GroupService
from app.database.user import User

router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

# 🔸 POST /groups/ - Create new group
@router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED, name="create_group")
def create_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    group = GroupService.create_group(db, group_data)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group name already exists"
        )
    return group

# 🔸 GET /groups/ - List all groups
@router.get("/", response_model=list[GroupOut], name="get_all_groups")
def get_all_groups(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    return GroupService.get_all_groups(
        db,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )

# 🔸 GET /groups/{id} - Get group by ID
@router.get("/{id}", response_model=GroupOut, name="get_group")
def get_group(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    group = GroupService.get_group_by_id(db, id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return group

# 🔸 PUT /groups/{id} - Update group
@router.put("/{id}", response_model=GroupOut, name="update_group")
def update_group(
    id: int,
    group_data: GroupUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    group = GroupService.update_group(db, id, group_data)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return group

# 🔸 DELETE /groups/{id} - Delete group (soft delete)
@router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED, name="delete_group")
def delete_group(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    if not GroupService.delete_group(db, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return {"message": "Group deleted"}

# 🔸 GET /groups/name/{name} - Get group by name
@router.get("/name/{name}", response_model=GroupOut, name="get_group_by_name")
def get_group_by_name(
    name: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)  # Requires authentication
):
    group = GroupService.get_group_by_name(db, name)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return group
