from datetime import datetime,timezone
from fastapi import APIRouter, Depends, HTTPException, Path, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated
from sqlalchemy import select, func, or_, desc, asc
from sqlalchemy.orm import joinedload

from app.api.dependencies.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut, UsersResponse
from app.database.services.user_service import UserService
from app.database.models import User, Role, Group
from app.api.dependencies.auth import get_current_user, require_permission
from app.utils.logger import log

router = APIRouter(prefix="/users", tags=["Users"])

# 🔸 POST /users/ - Register a new user (async)
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED, name="create_user")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await UserService.create_user(db, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    log.info("User created", user_id=user.id, username=user.username, email=user.email)
    return user

# 🔸 GET /users/me - Get current user profile (async)
@router.get("/me", response_model=UserOut, name="get_me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# 🔸 PUT /users/me - Update current user (async)
@router.put("/me", response_model=UserOut, name="put_me")
async def update_me(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    response = await UserService.update_user(db, current_user.id, user_data)
    log.info("User updated", user_id=current_user.id, username=current_user.username, email=current_user.email)
    return response

# 🔸 DELETE /users/me - Soft delete current user (async)
@router.delete("/me", status_code=status.HTTP_202_ACCEPTED, name="delete_me")
async def delete_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id
    username = current_user.username
    email = current_user.email
    await UserService.delete_user(db, current_user.id)
    log.info("User deleted", user_id=user_id, username=username, email=email)
    return {"Message": "User Deleted."}
    
@router.get("/get_all_users", response_model=UsersResponse, dependencies=[require_permission("search_user")])
async def get_all_users(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    sort: Annotated[Optional[str], Query()] = "created",
    order: Annotated[Optional[str], Query()] = "desc",
    status: Optional[bool] = Query(True, description="Filter by user status"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    group: Optional[str] = Query(None, description="Filter by user group"),
    search: Optional[str] = Query(None, description="Search term on username or email"),
    session: AsyncSession = Depends(get_db)      # DB session
):
    total, users = await UserService.get_all_users(
        db=session,
        page=page,
        limit=limit,
        sort_by=sort,
        sort_order=order,
        status=status,
        role=role,
        group=group,
        search=search
    )
    # Convert ORM objects to Pydantic schemas
    users_data = [UserOut.model_validate(u) for u in users]
    # Assemble full paginated response
    return UsersResponse(
        page=page,
        limit=limit,
        total=total,
        users=users_data
    )

# 🔸 GET /users/{id} - Admin only access to fetch any user (async)
@router.get("/{id}", response_model=UserOut, name="get_by_id", dependencies=[require_permission("search_user")])
async def get_user_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    user = await UserService.get_user_by_id(db, id)
    if user:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found.",
        )
        
@router.post("/{user_id}/activate", status_code=status.HTTP_200_OK, dependencies=[require_permission("activate_user")])
async def activate_user(
    user_id: int = Path(..., title="User ID to activate"),
    db: AsyncSession = Depends(get_db),
):
    success = await UserService.activate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activation failed. User may already be active or not exist.",
        )
    updated_at = datetime.now(tz=timezone.utc).isoformat()
    log.info("User activated", user_id=user_id, updated_at=updated_at)
    return {"status": "active", "updated_at": updated_at}

@router.post("/{user_id}/deactivate", status_code=status.HTTP_200_OK, dependencies=[require_permission("deactivate_user")])
async def deactivate_user(
    user_id: int = Path(..., title="User ID to deactivate"),
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    success = await UserService.deactivate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deactivation failed. User may already be inactive or not exist.",
        )
    updated_at = datetime.now(tz=timezone.utc).isoformat()
    log.info("User deactivated", user_id=user_id, updated_at=updated_at, reason=reason)
    return {"status": "inactive", "updated_at": updated_at}

@router.get("/{user_id}/activity_logs", dependencies=[require_permission("view_audit_logs")])
async def get_user_activity_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user_id: int = Path(..., title="User ID to fetch activity logs for"),
    db: AsyncSession = Depends(get_db),
):
    logs, total = await UserService.get_users_activity_logs(db=db, user_id=user_id, limit=limit, offset=offset)
    if logs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or no activity logs available.",
        )
    return {
        "user_id": user_id,
        "total": total,
        "limit": int(limit),
        "offset": int(offset),
        "activities": logs
        }