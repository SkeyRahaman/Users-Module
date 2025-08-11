from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.models import Role
from app.schemas.role import RoleCreate, RoleUpdate

class RoleService:

    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Role | None:
        """Create a new role. Returns None if role name exists or on error."""
        if RoleService.check_name_exists(db, role_data.name):
            return None

        role = Role(
            name=role_data.name,
            description=role_data.description
        )
        db.add(role)
        try:
            db.commit()
            db.refresh(role)
            return role
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def update_role(db: Session, role_id: int, role_data: RoleUpdate) -> Role | None:
        """Update an existing role. Returns None if role not found."""
        role = db.query(Role).filter(
            Role.id == role_id,
            Role.is_deleted == False
        ).first()
        
        if not role:
            return None

        for field, value in role_data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)

        try:
            db.commit()
            db.refresh(role)
            return role
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        """Soft delete a role. Returns False if role not found."""
        role = db.query(Role).filter(
            Role.id == role_id,
            Role.is_deleted == False
        ).first()
        
        if not role:
            return False

        role.is_deleted = True
        try:
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False

    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Role | None:
        """Get role by ID. Returns None if not found or deleted."""
        return db.query(Role).filter(
            Role.id == role_id,
            Role.is_deleted == False
        ).first()

    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Role | None:
        """Get role by name. Returns None if not found or deleted."""
        return db.query(Role).filter(
            Role.name == name,
            Role.is_deleted == False
        ).first()

    @staticmethod
    def get_all_roles(
            db: Session,
            skip: int = 0,
            limit: int = 10,
            sort_by: str = "created",
            sort_order: str = "desc"
        ) -> list[Role]:
        """
        Retrieve paginated and sorted list of active roles.
        Returns empty list if sort field is invalid.
        """
        if not hasattr(Role, sort_by):
            return []

        order_by_clause = desc(getattr(Role, sort_by)) if sort_order == "desc" else asc(getattr(Role, sort_by))

        return (
            db.query(Role)
            .filter(Role.is_deleted == False)
            .order_by(order_by_clause)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def check_name_exists(db: Session, name: str) -> bool:
        """Check if role name already exists (excluding deleted roles)."""
        return db.query(Role).filter(
            Role.name == name,
            Role.is_deleted == False
        ).first() is not None
    