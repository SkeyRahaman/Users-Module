import pytest
from fastapi import HTTPException, status
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.api.routers import permissions as permission_router
from app.database.services.permission_service import PermissionService
from app.schemas.permission import PermissionCreate, PermissionUpdate

# --- Fixtures ---
@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def mock_permission():
    permission = Mock()
    permission.id = 1
    permission.name = "test_permission"
    permission.description = "Test description"
    permission.is_deleted = False
    return permission

# --- Tests ---
class TestPermissionRouter:
    def test_create_permission_success(self, mock_db, mock_permission):
        # Arrange
        with patch.object(PermissionService, "create_permission", return_value=mock_permission):
            permission_data = PermissionCreate(
                name="test_permission",
                description="Test description"
            )
            
            # Act
            result = permission_router.create_permission(permission_data, mock_db, Mock())
            
            # Assert
            assert result.id == 1
            assert result.name == "test_permission"

    def test_create_permission_duplicate(self, mock_db):
        # Arrange
        with patch.object(PermissionService, "create_permission", return_value=None):
            permission_data = PermissionCreate(
                name="duplicate",
                description="Should fail"
            )
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                permission_router.create_permission(permission_data, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "already exists" in exc_info.value.detail

    def test_get_permission_success(self, mock_db, mock_permission):
        # Arrange
        with patch.object(PermissionService, "get_permission_by_id", return_value=mock_permission):
            # Act
            result = permission_router.get_permission(1, mock_db, Mock())
            
            # Assert
            assert result.id == 1
            assert result.name == "test_permission"

    def test_get_permission_not_found(self, mock_db):
        # Arrange
        with patch.object(PermissionService, "get_permission_by_id", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                permission_router.get_permission(999, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_update_permission_success(self, mock_db, mock_permission):
        # Arrange
        update_data = PermissionUpdate(description="Updated description")
        with patch.object(PermissionService, "update_permission", return_value=mock_permission):
            # Act
            result = permission_router.update_permission(1, update_data, mock_db, Mock())
            
            # Assert
            assert result.id == 1
            assert result.description == "Test description"  # Mock returns original

    def test_update_permission_not_found(self, mock_db):
        # Arrange
        update_data = PermissionUpdate(description="Should fail")
        with patch.object(PermissionService, "update_permission", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                permission_router.update_permission(999, update_data, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_permission_success(self, mock_db):
        # Arrange
        with patch.object(PermissionService, "delete_permission", return_value=True):
            # Act
            result = permission_router.delete_permission(1, mock_db, Mock())
            
            # Assert
            assert result["message"] == "Permission deleted"

    def test_delete_permission_not_found(self, mock_db):
        # Arrange
        with patch.object(PermissionService, "delete_permission", return_value=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                permission_router.delete_permission(999, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_get_all_permissions(self, mock_db, mock_permission):
        # Arrange
        with patch.object(PermissionService, "get_all_permissions", return_value=[mock_permission]):
            # Act
            result = permission_router.get_all_permissions(0, 10, "created", "desc", mock_db, Mock())
            
            # Assert
            assert len(result) == 1
            assert result[0].name == "test_permission"