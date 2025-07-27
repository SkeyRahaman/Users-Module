import pytest
from fastapi import HTTPException, status
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.api.routers import groups as group_router
from app.services.group_service import GroupService
from app.schemas.group import GroupCreate, GroupUpdate

# --- Fixtures ---
@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def mock_group():
    group = Mock()
    group.id = 1
    group.name = "test_group"
    group.description = "Test description"
    group.is_deleted = False
    return group

# --- Tests ---
class TestGroupRouter:
    def test_create_group_success(self, mock_db, mock_group):
        # Arrange
        with patch.object(GroupService, "create_group", return_value=mock_group):
            group_data = GroupCreate(
                name="test_group",
                description="Test description"
            )
            
            # Act
            result = group_router.create_group(group_data, mock_db, Mock())
            
            # Assert
            assert result.id == 1
            assert result.name == "test_group"

    def test_create_group_duplicate(self, mock_db):
        # Arrange
        with patch.object(GroupService, "create_group", return_value=None):
            group_data = GroupCreate(
                name="duplicate",
                description="Should fail"
            )
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                group_router.create_group(group_data, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "already exists" in exc_info.value.detail

    def test_get_group_success(self, mock_db, mock_group):
        # Arrange
        with patch.object(GroupService, "get_group_by_id", return_value=mock_group):
            # Act
            result = group_router.get_group(1, mock_db, Mock())
            
            # Assert
            assert result.id == 1
            assert result.name == "test_group"

    def test_get_group_not_found(self, mock_db):
        # Arrange
        with patch.object(GroupService, "get_group_by_id", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                group_router.get_group(999, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_update_group_success(self, mock_db, mock_group):
        # Arrange
        update_data = GroupUpdate(description="Updated description")
        with patch.object(GroupService, "update_group", return_value=mock_group):
            # Act
            result = group_router.update_group(1, update_data, mock_db, Mock())
            
            # Assert
            assert result.id == 1
            assert result.description == "Test description"  # Mock returns original

    def test_update_group_not_found(self, mock_db):
        # Arrange
        update_data = GroupUpdate(description="Should fail")
        with patch.object(GroupService, "update_group", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                group_router.update_group(999, update_data, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_group_success(self, mock_db):
        # Arrange
        with patch.object(GroupService, "delete_group", return_value=True):
            # Act
            result = group_router.delete_group(1, mock_db, Mock())
            
            # Assert
            assert result["message"] == "Group deleted"

    def test_delete_group_not_found(self, mock_db):
        # Arrange
        with patch.object(GroupService, "delete_group", return_value=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                group_router.delete_group(999, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_get_all_groups(self, mock_db, mock_group):
        # Arrange
        with patch.object(GroupService, "get_all_groups", return_value=[mock_group]):
            # Act
            result = group_router.get_all_groups(0, 10, "created", "desc", mock_db, Mock())
            
            # Assert
            assert len(result) == 1
            assert result[0].name == "test_group"

    def test_get_group_by_name_success(self, mock_db, mock_group):
        # Arrange
        with patch.object(GroupService, "get_group_by_name", return_value=mock_group):
            # Act
            result = group_router.get_group_by_name("test_group", mock_db, Mock())
            
            # Assert
            assert result.id == 1
            assert result.name == "test_group"

    def test_get_group_by_name_not_found(self, mock_db):
        # Arrange
        with patch.object(GroupService, "get_group_by_name", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                group_router.get_group_by_name("nonexistent", mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_get_all_groups_pagination(self, mock_db, mock_group):
        # Arrange
        mock_groups = [mock_group] * 5
        with patch.object(GroupService, "get_all_groups", return_value=mock_groups):
            # Act
            result = group_router.get_all_groups(skip=2, limit=5, db=mock_db)
            
            # Assert
            assert len(result) == 5
            GroupService.get_all_groups.assert_called_once_with(
                mock_db,
                skip=2,
                limit=5,
                sort_by="created",
                sort_order="desc"
            )

    def test_get_all_groups_sorting(self, mock_db, mock_group):
        # Arrange
        mock_groups = [mock_group] * 3
        with patch.object(GroupService, "get_all_groups", return_value=mock_groups):
            # Act
            result = group_router.get_all_groups(
                sort_by="name",
                sort_order="asc",
                db=mock_db
            )
            
            # Assert
            assert len(result) == 3
            GroupService.get_all_groups.assert_called_once_with(
                mock_db,
                skip=0,
                limit=10,
                sort_by="name",
                sort_order="asc"
            )
