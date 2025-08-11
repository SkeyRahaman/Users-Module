import pytest
from sqlalchemy.orm import Session

from app.database.services.group_service import GroupService
from app.schemas.group import GroupCreate, GroupUpdate
from app.database.models import Group

class TestGroupService:
    """Test class for GroupService"""

    def test_create_group_success(self, db_session: Session):
        # Arrange
        group_data = GroupCreate(
            name="developers",
            description="Development team"
        )

        # Act
        result = GroupService.create_group(db_session, group_data)

        # Assert
        assert result is not None
        assert result.id is not None
        assert result.name == "developers"
        assert result.description == "Development team"
        assert result.is_deleted is False

    def test_create_duplicate_group_fails(self, db_session: Session):
        # Arrange - Create first group
        group1 = GroupCreate(name="managers", description="Management team")
        GroupService.create_group(db_session, group1)

        # Act - Try to create duplicate
        group2 = GroupCreate(name="managers", description="Different description")
        result = GroupService.create_group(db_session, group2)

        # Assert
        assert result is None

    def test_get_group_by_id(self, db_session: Session):
        # Arrange
        group_data = GroupCreate(name="qa", description="Quality Assurance")
        created_group = GroupService.create_group(db_session, group_data)

        # Act
        fetched_group = GroupService.get_group_by_id(db_session, created_group.id)

        # Assert
        assert fetched_group is not None
        assert fetched_group.id == created_group.id
        assert fetched_group.name == "qa"

    def test_get_nonexistent_group(self, db_session: Session):
        # Act
        result = GroupService.get_group_by_id(db_session, 99999)

        # Assert
        assert result is None

    def test_update_group(self, db_session: Session):
        # Arrange
        original = GroupCreate(name="designers", description="Design team")
        created = GroupService.create_group(db_session, original)
        update_data = GroupUpdate(description="Updated design team description")

        # Act
        updated = GroupService.update_group(db_session, created.id, update_data)

        # Assert
        assert updated is not None
        assert updated.description == "Updated design team description"
        assert updated.name == "designers"  # Unchanged
        assert updated.id == created.id

    def test_delete_group(self, db_session: Session):
        # Arrange
        group = GroupCreate(name="marketing", description="Marketing team")
        created = GroupService.create_group(db_session, group)

        # Act
        delete_result = GroupService.delete_group(db_session, created.id)
        fetched_after_delete = GroupService.get_group_by_id(db_session, created.id)

        # Assert
        assert delete_result is True
        assert fetched_after_delete is None

    def test_get_all_groups(self, db_session: Session):
        # Arrange - Create test data
        groups = [
            GroupCreate(name=f"group_{i}", description=f"Group {i}")
            for i in range(1, 6)
        ]
        for group in groups:
            GroupService.create_group(db_session, group)

        # Act
        result = GroupService.get_all_groups(db_session)

        # Assert
        assert len(result) == 5
        assert all(isinstance(g, Group) for g in result)
        assert sorted([g.name for g in result]) == [f"group_{i}" for i in range(1, 6)]

    def test_check_name_exists(self, db_session: Session):
        # Arrange
        group = GroupCreate(name="finance", description="Finance department")
        GroupService.create_group(db_session, group)

        # Act & Assert
        assert GroupService.check_name_exists(db_session, "finance") is True
        assert GroupService.check_name_exists(db_session, "nonexistent_group") is False

    def test_get_all_groups_pagination(self, db_session: Session):
        # Arrange - Create test data
        groups = [
            GroupCreate(name=f"paged_group_{i}", description=f"Group {i}")
            for i in range(1, 21)
        ]
        for group in groups:
            GroupService.create_group(db_session, group)

        # Act - Get first page
        page1 = GroupService.get_all_groups(db_session, skip=0, limit=10)
        # Act - Get second page
        page2 = GroupService.get_all_groups(db_session, skip=10, limit=10)

        # Assert
        assert len(page1) == 10
        assert len(page2) == 10
        assert all(g.name.startswith("paged_group_") for g in page1 + page2)
        assert set(g.name for g in page1).isdisjoint(set(g.name for g in page2))

    def test_get_all_groups_sorting(self, db_session: Session):
        # Arrange - Create test data with different creation times
        group1 = GroupCreate(name="group_b", description="Earlier group")
        created1 = GroupService.create_group(db_session, group1)
        
        group2 = GroupCreate(name="group_a", description="Later group")
        created2 = GroupService.create_group(db_session, group2)

        # Act - Sort by name ascending
        sorted_asc = GroupService.get_all_groups(db_session, sort_by="name", sort_order="asc")
        # Act - Sort by name descending
        sorted_desc = GroupService.get_all_groups(db_session, sort_by="name", sort_order="desc")

        # Assert
        assert [g.name for g in sorted_asc] == ["group_a", "group_b"]
        assert [g.name for g in sorted_desc] == ["group_b", "group_a"]

    def test_get_group_by_name(self, db_session: Session):
        # Arrange
        group_data = GroupCreate(name="hr", description="Human Resources")
        created_group = GroupService.create_group(db_session, group_data)

        # Act
        fetched_group = GroupService.get_group_by_name(db_session, "hr")

        # Assert
        assert fetched_group is not None
        assert fetched_group.id == created_group.id
        assert fetched_group.name == "hr"

    def test_get_invalid_sort_field_returns_empty(self, db_session: Session):
        # Arrange
        group = GroupCreate(name="test_group", description="Test")
        GroupService.create_group(db_session, group)

        # Act
        result = GroupService.get_all_groups(db_session, sort_by="invalid_field")

        # Assert
        assert result == []
