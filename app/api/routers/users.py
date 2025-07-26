from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.user_service import UserService
from app.api.dependencies.auth import get_current_user
from app.database.user import User

router = APIRouter(prefix="/users", tags=["Users"])

# 🔸 POST /users/ - Register a new user
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED, name="create_user")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = UserService.create_user(db, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    return user


# 🔸 GET /users/me - Get current user profile
@router.get("/me", response_model=UserOut, name="get_me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# 🔸 PUT /users/me - Update current user
@router.put("/me", response_model=UserOut, name="put_me")
def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return UserService.update_user(db, current_user.id, user_data)


# 🔸 DELETE /users/me - Soft delete current user
@router.delete("/me", status_code=status.HTTP_202_ACCEPTED, name="delete_me")
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    UserService.delete_user(db, current_user.id)
    return {"Message" : "User Deleted."}


# 🔸 GET /users/{id} - Admin only access to fetch any user
@router.get("/{id}", response_model=UserOut, name="get_by_id")
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    user = UserService.get_user_by_id(db, id)
    if user:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found.",
        )
