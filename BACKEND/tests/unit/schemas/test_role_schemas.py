import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.role import RoleBase, RoleCreate, RoleUpdate, RoleOut

class TestRoleBase:
    """Test cases for RoleBase model"""
    
    def test_valid_role_base(self):
        """Test valid RoleBase creation"""
        role = RoleBase(
            name="admin",
            description="Administrator role"
        )
        assert role.name == "admin"
        assert role.description == "Administrator role"
    
    def test_minimal_role_base(self):
        """Test RoleBase with minimal required fields"""
        role = RoleBase(name="editor")
        assert role.name == "editor"
        assert role.description is None
    
    def test_invalid_role_base_missing_name(self):
        """Test RoleBase with missing required field"""
        with pytest.raises(ValidationError):
            RoleBase(description="Missing name")

class TestRoleCreate:
    """Test cases for RoleCreate model"""
    
    def test_role_create_inheritance(self):
        """Test that RoleCreate inherits from RoleBase"""
        role = RoleCreate(
            name="moderator",
            description="Content moderator"
        )
        assert isinstance(role, RoleBase)
        assert role.name == "moderator"
    
    def test_role_create_identical_to_base(self):
        """Test that RoleCreate has same fields as RoleBase"""
        base_fields = RoleBase.model_fields
        create_fields = RoleCreate.model_fields
        assert base_fields.keys() == create_fields.keys()

class TestRoleUpdate:
    """Test cases for RoleUpdate model"""
    
    def test_role_update_all_optional(self):
        """Test that all fields in RoleUpdate are optional"""
        role = RoleUpdate()
        assert role.name is None
        assert role.description is None
    
    def test_partial_role_update(self):
        """Test updating just one field"""
        role = RoleUpdate(name="new_role_name")
        assert role.name == "new_role_name"
        assert role.description is None
        
        role = RoleUpdate(description="new_description")
        assert role.name is None
        assert role.description == "new_description"
    
    def test_full_role_update(self):
        """Test updating all fields"""
        role = RoleUpdate(
            name="updated_role",
            description="updated description"
        )
        assert role.name == "updated_role"
        assert role.description == "updated description"

class TestRoleOut:
    """Test cases for RoleOut model"""
    
    @pytest.fixture
    def sample_datetime(self):
        return datetime(2023, 1, 1, 12, 0, 0)
    
    def test_role_out_required_fields(self, sample_datetime):
        """Test required fields in RoleOut"""
        role = RoleOut(
            id=1,
            name="admin",
            created=sample_datetime,
            updated=sample_datetime,
            is_deleted=False
        )
        assert role.id == 1
        assert role.name == "admin"
        assert role.created == sample_datetime
        assert role.updated == sample_datetime
        assert role.is_deleted is False
    
    def test_role_out_optional_fields(self, sample_datetime):
        """Test optional fields in RoleOut"""
        role = RoleOut(
            id=1,
            name="editor",
            created=sample_datetime,
            updated=None,
            is_deleted=None
        )
        assert role.updated is None
        assert role.is_deleted is None
    
    def test_role_out_inherits_base(self, sample_datetime):
        """Test that RoleOut includes base fields"""
        role = RoleOut(
            id=1,
            name="viewer",
            description="Read-only access",
            created=sample_datetime,
            updated=sample_datetime,
            is_deleted=False
        )
        assert role.description == "Read-only access"
    
    def test_role_out_from_attributes(self, sample_datetime):
        """Test the from_attributes configuration"""
        class DBModel:
            def __init__(self):
                self.id = 1
                self.name = "db_role"
                self.description = "from database"
                self.created = sample_datetime
                self.updated = sample_datetime
                self.is_deleted = True
        
        db_instance = DBModel()
        role = RoleOut.model_validate(db_instance)
        
        assert role.id == 1
        assert role.name == "db_role"
        assert role.description == "from database"
        assert role.created == sample_datetime
        assert role.is_deleted is True