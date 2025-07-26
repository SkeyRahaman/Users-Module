import pytest
from sqlalchemy.orm import Session

from app.services.permission_service import PermissionService
from app.schemas.permission import PermissionCreate, PermissionUpdate
from app.database.permission import Permission

class TestPermissionService:
    """Test class for PermissionService"""

    def test_create_permission_success(self, db_session: Session):
        # Arrange
        permission_data = PermissionCreate(
            name="create_post",
            description="Can create new posts"
        )

        # Act
        result = PermissionService.create_permission(db_session, permission_data)

        # Assert
        assert result is not None
        assert result.id is not None
        assert result.name == "create_post"
        assert result.description == "Can create new posts"
        assert result.is_deleted is False

    def test_create_duplicate_permission_fails(self, db_session: Session):
        # Arrange - Create first permission
        perm1 = PermissionCreate(name="edit_post", description="Can edit posts")
        PermissionService.create_permission(db_session, perm1)

        # Act - Try to create duplicate
        perm2 = PermissionCreate(name="edit_post", description="Different description")
        result = PermissionService.create_permission(db_session, perm2)

        # Assert
        assert result is None

    def test_get_permission_by_id(self, db_session: Session):
        # Arrange
        perm_data = PermissionCreate(name="delete_post", description="Can delete posts")
        created_perm = PermissionService.create_permission(db_session, perm_data)

        # Act
        fetched_perm = PermissionService.get_permission_by_id(db_session, created_perm.id)

        # Assert
        assert fetched_perm is not None
        assert fetched_perm.id == created_perm.id
        assert fetched_perm.name == "delete_post"

    def test_get_nonexistent_permission(self, db_session: Session):
        # Act
        result = PermissionService.get_permission_by_id(db_session, 99999)

        # Assert
        assert result is None

    def test_update_permission(self, db_session: Session):
        # Arrange
        original = PermissionCreate(name="view_post", description="Original")
        created = PermissionService.create_permission(db_session, original)
        update_data = PermissionUpdate(description="Updated description")

        # Act
        updated = PermissionService.update_permission(db_session, created.id, update_data)

        # Assert
        assert updated is not None
        assert updated.description == "Updated description"
        assert updated.name == "view_post"  # Unchanged
        assert updated.id == created.id

    def test_delete_permission(self, db_session: Session):
        # Arrange
        perm = PermissionCreate(name="publish_post", description="Can publish")
        created = PermissionService.create_permission(db_session, perm)

        # Act
        delete_result = PermissionService.delete_permission(db_session, created.id)
        fetched_after_delete = PermissionService.get_permission_by_id(db_session, created.id)

        # Assert
        assert delete_result is True
        assert fetched_after_delete is None

    def test_get_all_permissions(self, db_session: Session):
        # Arrange - Create test data
        permissions = [
            PermissionCreate(name=f"perm_{i}", description=f"Permission {i}")
            for i in range(1, 6)
        ]
        for perm in permissions:
            PermissionService.create_permission(db_session, perm)

        # Act
        result = PermissionService.get_all_permissions(db_session)

        # Assert
        assert len(result) == 5
        assert all(isinstance(p, Permission) for p in result)
        assert sorted([p.name for p in result]) == [f"perm_{i}" for i in range(1, 6)]

    def test_check_name_exists(self, db_session: Session):
        # Arrange
        perm = PermissionCreate(name="unique_perm", description="Test")
        PermissionService.create_permission(db_session, perm)

        # Act & Assert
        assert PermissionService.check_name_exists(db_session, "unique_perm") is True
        assert PermissionService.check_name_exists(db_session, "nonexistent") is False