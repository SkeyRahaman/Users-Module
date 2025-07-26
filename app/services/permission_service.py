from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate

class PermissionService:

    @staticmethod
    def create_permission(db: Session, permission_data: PermissionCreate) -> Permission | None:
        if PermissionService.check_name_exists(db, permission_data.name):
            return None

        permission = Permission(
            name=permission_data.name,
            description=permission_data.description
        )
        db.add(permission)
        try:
            db.commit()
            db.refresh(permission)
            return permission
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def update_permission(db: Session, permission_id: int, permission_data: PermissionUpdate) -> Permission | None:
        permission = db.query(Permission).filter(
            Permission.id == permission_id,
            Permission.is_deleted == False
        ).first()
        
        if not permission:
            return None

        for field, value in permission_data.model_dump(exclude_unset=True).items():
            setattr(permission, field, value)

        try:
            db.commit()
            db.refresh(permission)
            return permission
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def delete_permission(db: Session, permission_id: int) -> bool:
        permission = db.query(Permission).filter(
            Permission.id == permission_id,
            Permission.is_deleted == False
        ).first()
        
        if not permission:
            return False

        permission.is_deleted = True
        try:
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False

    @staticmethod
    def get_permission_by_id(db: Session, permission_id: int) -> Permission | None:
        return db.query(Permission).filter(
            Permission.id == permission_id,
            Permission.is_deleted == False
        ).first()

    @staticmethod
    def get_permission_by_name(db: Session, name: str) -> Permission | None:
        return db.query(Permission).filter(
            Permission.name == name,
            Permission.is_deleted == False
        ).first()

    @staticmethod
    def get_all_permissions(
            db: Session,
            skip: int = 0,
            limit: int = 10,
            sort_by: str = "created",
            sort_order: str = "desc"
        ) -> list[Permission]:
        """
        Retrieve a paginated and sorted list of active permissions.
        Returns empty list if sort field is invalid.
        """
        if not hasattr(Permission, sort_by):
            return []

        order_by_clause = desc(getattr(Permission, sort_by)) if sort_order == "desc" else asc(getattr(Permission, sort_by))

        return (
            db.query(Permission)
            .filter(Permission.is_deleted == False)
            .order_by(order_by_clause)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def check_name_exists(db: Session, name: str) -> bool:
        return db.query(Permission).filter(
            Permission.name == name,
            Permission.is_deleted == False
        ).first() is not None
    