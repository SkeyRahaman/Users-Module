from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.group import Group
from app.schemas.group import GroupCreate, GroupUpdate

class GroupService:
    """Service layer for group operations"""

    @staticmethod
    def create_group(db: Session, group_data: GroupCreate) -> Group | None:
        """Create a new group if name doesn't already exist"""
        if GroupService.check_name_exists(db, group_data.name):
            return None

        group = Group(
            name=group_data.name,
            description=group_data.description
        )
        db.add(group)
        try:
            db.commit()
            db.refresh(group)
            return group
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def update_group(db: Session, group_id: int, group_data: GroupUpdate) -> Group | None:
        """Update an existing group"""
        group = db.query(Group).filter(
            Group.id == group_id,
            Group.is_deleted == False
        ).first()
        
        if not group:
            return None

        for field, value in group_data.model_dump(exclude_unset=True).items():
            setattr(group, field, value)

        try:
            db.commit()
            db.refresh(group)
            return group
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def delete_group(db: Session, group_id: int) -> bool:
        """Soft delete a group"""
        group = db.query(Group).filter(
            Group.id == group_id,
            Group.is_deleted == False
        ).first()
        
        if not group:
            return False

        group.is_deleted = True
        try:
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False

    @staticmethod
    def get_group_by_id(db: Session, group_id: int) -> Group | None:
        """Get group by ID excluding deleted groups"""
        return db.query(Group).filter(
            Group.id == group_id,
            Group.is_deleted == False
        ).first()

    @staticmethod
    def get_group_by_name(db: Session, name: str) -> Group | None:
        """Get group by name excluding deleted groups"""
        return db.query(Group).filter(
            Group.name == name,
            Group.is_deleted == False
        ).first()

    @staticmethod
    def get_all_groups(
            db: Session,
            skip: int = 0,
            limit: int = 10,
            sort_by: str = "created",
            sort_order: str = "desc"
        ) -> list[Group]:
        """
        Get paginated and sorted list of active groups
        Returns empty list if sort field is invalid
        """
        if not hasattr(Group, sort_by):
            return []

        order_by_clause = desc(getattr(Group, sort_by)) if sort_order == "desc" else asc(getattr(Group, sort_by))

        return (
            db.query(Group)
            .filter(Group.is_deleted == False)
            .order_by(order_by_clause)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def check_name_exists(db: Session, name: str) -> bool:
        """Check if group name exists (excluding deleted groups)"""
        return db.query(Group).filter(
            Group.name == name,
            Group.is_deleted == False
        ).first() is not None
