from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.auth.password import PasswordHasher

class UserService:

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User | None:
        if UserService.check_username_exists(db, user_data.username):
            return None

        if UserService.check_email_exists(db, user_data.email):
            return None

        hashed_password = PasswordHasher.get_password_hash(user_data.password)
        user = User(
            firstname=user_data.firstname,
            middlename=user_data.middlename,
            lastname=user_data.lastname,
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User | None:
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            return None

        for field, value in user_data.model_dump(exclude_unset=True).items():
            if field == "password" and value:
                setattr(user, field, PasswordHasher.get_password_hash(value))
            else:
                setattr(user, field, value)

        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            return False

        user.is_deleted = True
        try:
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id, User.is_deleted == False).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_all_users(
            db: Session,
            skip: int = 0,
            limit: int = 10,
            sort_by: str = "created",
            sort_order: str = "desc"
        ) -> list[User]:
        """
        Retrieve a paginated and sorted list of active (non-deleted) users.
        Returns empty list if sort field is invalid.
        """
        if not hasattr(User, sort_by):
            return []

        order_by_clause = desc(getattr(User, sort_by)) if sort_order == "desc" else asc(getattr(User, sort_by))

        return (
            db.query(User)
            .filter(User.is_deleted == False)
            .order_by(order_by_clause)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def check_username_exists(db: Session, username: str) -> bool:
        return db.query(User).filter(User.username == username, User.is_deleted == False).first() is not None

    @staticmethod
    def check_email_exists(db: Session, email: str) -> bool:
        return db.query(User).filter(User.email == email, User.is_deleted == False).first() is not None