import pytest
from sqlalchemy.orm import Session

from app.services.role_service import RoleService
from app.schemas.role import RoleCreate, RoleUpdate
from app.database.role import Role

class TestRoleService:
    """Test class for RoleService"""

    def test_create_role_success(self, db_session: Session):
        # Arrange
        role_data = RoleCreate(
            name="admin",
            description="Administrator role"
        )

        # Act
        result = RoleService.create_role(db_session, role_data)

        # Assert
        assert result is not None
        assert result.id is not None
        assert result.name == "admin"
        assert result.description == "Administrator role"
        assert result.is_deleted is False

    def test_create_duplicate_role_fails(self, db_session: Session):
        # Arrange - Create first role
        role1 = RoleCreate(name="editor", description="Editor role")
        RoleService.create_role(db_session, role1)

        # Act - Try to create duplicate
        role2 = RoleCreate(name="editor", description="Different description")
        result = RoleService.create_role(db_session, role2)

        # Assert
        assert result is None

    def test_get_role_by_id(self, db_session: Session):
        # Arrange
        role_data = RoleCreate(name="viewer", description="Viewer role")
        created_role = RoleService.create_role(db_session, role_data)

        # Act
        fetched_role = RoleService.get_role_by_id(db_session, created_role.id)

        # Assert
        assert fetched_role is not None
        assert fetched_role.id == created_role.id
        assert fetched_role.name == "viewer"

    def test_get_nonexistent_role(self, db_session: Session):
        # Act
        result = RoleService.get_role_by_id(db_session, 99999)

        # Assert
        assert result is None

    def test_update_role(self, db_session: Session):
        # Arrange
        original = RoleCreate(name="moderator", description="Original description")
        created = RoleService.create_role(db_session, original)
        update_data = RoleUpdate(description="Updated description")

        # Act
        updated = RoleService.update_role(db_session, created.id, update_data)

        # Assert
        assert updated is not None
        assert updated.description == "Updated description"
        assert updated.name == "moderator"  # Unchanged
        assert updated.id == created.id

    def test_delete_role(self, db_session: Session):
        # Arrange
        role = RoleCreate(name="guest", description="Guest role")
        created = RoleService.create_role(db_session, role)

        # Act
        delete_result = RoleService.delete_role(db_session, created.id)
        fetched_after_delete = RoleService.get_role_by_id(db_session, created.id)

        # Assert
        assert delete_result is True
        assert fetched_after_delete is None

    def test_get_all_roles(self, db_session: Session):
        # Arrange - Create test data
        roles = [
            RoleCreate(name=f"role_{i}", description=f"Role {i}")
            for i in range(1, 6)
        ]
        for role in roles:
            RoleService.create_role(db_session, role)

        # Act
        result = RoleService.get_all_roles(db_session)

        # Assert
        assert len(result) == 5
        assert all(isinstance(r, Role) for r in result)
        assert sorted([r.name for r in result]) == [f"role_{i}" for i in range(1, 6)]

    def test_check_name_exists(self, db_session: Session):
        # Arrange
        role = RoleCreate(name="special_role", description="Test")
        RoleService.create_role(db_session, role)

        # Act & Assert
        assert RoleService.check_name_exists(db_session, "special_role") is True
        assert RoleService.check_name_exists(db_session, "nonexistent_role") is False

    def test_get_all_roles_pagination(self, db_session: Session):
        # Arrange - Create test data
        roles = [
            RoleCreate(name=f"paged_role_{i}", description=f"Role {i}")
            for i in range(1, 21)
        ]
        for role in roles:
            RoleService.create_role(db_session, role)

        # Act - Get first page
        page1 = RoleService.get_all_roles(db_session, skip=0, limit=10)
        # Act - Get second page
        page2 = RoleService.get_all_roles(db_session, skip=10, limit=10)

        # Assert
        assert len(page1) == 10
        assert len(page2) == 10
        assert all(r.name.startswith("paged_role_") for r in page1 + page2)
        assert set(r.name for r in page1).isdisjoint(set(r.name for r in page2))

    def test_get_all_roles_sorting(self, db_session: Session):
        # Arrange - Create test data with different creation times
        role1 = RoleCreate(name="role_b", description="Earlier role")
        created1 = RoleService.create_role(db_session, role1)
        
        role2 = RoleCreate(name="role_a", description="Later role")
        created2 = RoleService.create_role(db_session, role2)

        # Act - Sort by name ascending
        sorted_asc = RoleService.get_all_roles(db_session, sort_by="name", sort_order="asc")
        # Act - Sort by name descending
        sorted_desc = RoleService.get_all_roles(db_session, sort_by="name", sort_order="desc")

        # Assert
        assert [r.name for r in sorted_asc] == ["role_a", "role_b"]
        assert [r.name for r in sorted_desc] == ["role_b", "role_a"]
