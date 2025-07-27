import pytest
from fastapi import HTTPException, status
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.api.routers import roles as role_router
from app.services.role_service import RoleService
from app.schemas.role import RoleCreate, RoleUpdate

# --- Fixtures ---
@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def mock_role():
    role = Mock()
    role.id = 1
    role.name = "test_role"
    role.description = "Test description"
    role.is_deleted = False
    return role

# --- Tests ---
class TestRoleRouter:
    def test_create_role_success(self, mock_db, mock_role):
        # Arrange
        with patch.object(RoleService, "create_role", return_value=mock_role):
            role_data = RoleCreate(
                name="test_role",
                description="Test description"
            )
            
            # Act
            result = role_router.create_role(role_data, mock_db, Mock())
            
            # Assert
            assert result.id == 1
            assert result.name == "test_role"

    def test_create_role_duplicate(self, mock_db):
        # Arrange
        with patch.object(RoleService, "create_role", return_value=None):
            role_data = RoleCreate(
                name="duplicate",
                description="Should fail"
            )
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                role_router.create_role(role_data, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "already exists" in exc_info.value.detail

    def test_get_role_success(self, mock_db, mock_role):
        # Arrange
        with patch.object(RoleService, "get_role_by_id", return_value=mock_role):
            # Act
            result = role_router.get_role(1, mock_db, Mock())
            
            # Assert
            assert result.id == 1
            assert result.name == "test_role"

    def test_get_role_not_found(self, mock_db):
        # Arrange
        with patch.object(RoleService, "get_role_by_id", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                role_router.get_role(999, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_update_role_success(self, mock_db, mock_role):
        # Arrange
        update_data = RoleUpdate(description="Updated description")
        with patch.object(RoleService, "update_role", return_value=mock_role):
            # Act
            result = role_router.update_role(1, update_data, mock_db, Mock())
            
            # Assert
            assert result.id == 1
            assert result.description == "Test description"  # Mock returns original

    def test_update_role_not_found(self, mock_db):
        # Arrange
        update_data = RoleUpdate(description="Should fail")
        with patch.object(RoleService, "update_role", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                role_router.update_role(999, update_data, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_role_success(self, mock_db):
        # Arrange
        with patch.object(RoleService, "delete_role", return_value=True):
            # Act
            result = role_router.delete_role(1, mock_db, Mock())
            
            # Assert
            assert result["message"] == "Role deleted"

    def test_delete_role_not_found(self, mock_db):
        # Arrange
        with patch.object(RoleService, "delete_role", return_value=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                role_router.delete_role(999, mock_db, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_get_all_roles(self, mock_db, mock_role):
        # Arrange
        with patch.object(RoleService, "get_all_roles", return_value=[mock_role]):
            # Act
            result = role_router.get_all_roles(0, 10, "created", "desc", mock_db, Mock())
            
            # Assert
            assert len(result) == 1
            assert result[0].name == "test_role"

    def test_get_all_roles_pagination(self, mock_db, mock_role):
        # Arrange
        mock_roles = [mock_role] * 5
        with patch.object(RoleService, "get_all_roles", return_value=mock_roles):
            # Act
            result = role_router.get_all_roles(skip=2, limit=5, db=mock_db)
            
            # Assert
            assert len(result) == 5
            RoleService.get_all_roles.assert_called_once_with(
                mock_db,
                skip=2,
                limit=5,
                sort_by="created",
                sort_order="desc"
            )

    def test_get_all_roles_sorting(self, mock_db, mock_role):
        # Arrange
        mock_roles = [mock_role] * 3
        with patch.object(RoleService, "get_all_roles", return_value=mock_roles):
            # Act
            result = role_router.get_all_roles(
                sort_by="name",
                sort_order="asc",
                db=mock_db
            )
            
            # Assert
            assert len(result) == 3
            RoleService.get_all_roles.assert_called_once_with(
                mock_db,
                skip=0,
                limit=10,
                sort_by="name",
                sort_order="asc"
            )
