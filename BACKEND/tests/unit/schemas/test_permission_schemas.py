import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.permission import PermissionBase, PermissionCreate, PermissionUpdate, PermissionOut

class TestPermissionBase:
    """Test cases for PermissionBase model"""
    
    def test_valid_permission_base(self):
        """Test valid PermissionBase creation"""
        permission = PermissionBase(
            name="read_content",
            description="Can read content"
        )
        assert permission.name == "read_content"
        assert permission.description == "Can read content"
    
    def test_minimal_permission_base(self):
        """Test PermissionBase with minimal required fields"""
        permission = PermissionBase(name="write_content")
        assert permission.name == "write_content"
        assert permission.description is None
    
    def test_invalid_permission_base_missing_name(self):
        """Test PermissionBase with missing required field"""
        with pytest.raises(ValidationError):
            PermissionBase(description="Missing name")

class TestPermissionCreate:
    """Test cases for PermissionCreate model"""
    
    def test_permission_create_inheritance(self):
        """Test that PermissionCreate inherits from PermissionBase"""
        permission = PermissionCreate(
            name="edit_content",
            description="Can edit content"
        )
        assert isinstance(permission, PermissionBase)
        assert permission.name == "edit_content"
    
    def test_permission_create_identical_to_base(self):
        """Test that PermissionCreate has same fields as PermissionBase"""
        base_fields = PermissionBase.model_fields
        create_fields = PermissionCreate.model_fields
        assert base_fields.keys() == create_fields.keys()

class TestPermissionUpdate:
    """Test cases for PermissionUpdate model"""
    
    def test_permission_update_all_optional(self):
        """Test that all fields in PermissionUpdate are optional"""
        permission = PermissionUpdate()
        assert permission.name is None
        assert permission.description is None
    
    def test_partial_permission_update(self):
        """Test updating just one field"""
        permission = PermissionUpdate(name="new_name")
        assert permission.name == "new_name"
        assert permission.description is None
        
        permission = PermissionUpdate(description="new_desc")
        assert permission.name is None
        assert permission.description == "new_desc"
    
    def test_full_permission_update(self):
        """Test updating all fields"""
        permission = PermissionUpdate(
            name="full_update",
            description="updated description"
        )
        assert permission.name == "full_update"
        assert permission.description == "updated description"

class TestPermissionOut:
    """Test cases for PermissionOut model"""
    
    @pytest.fixture
    def sample_datetime(self):
        return datetime(2023, 1, 1, 12, 0, 0)
    
    def test_permission_out_required_fields(self, sample_datetime):
        """Test required fields in PermissionOut"""
        permission = PermissionOut(
            id=1,
            name="out_permission",
            created=sample_datetime,
            updated=sample_datetime
        )
        assert permission.id == 1
        assert permission.name == "out_permission"
        assert permission.created == sample_datetime
        assert permission.updated == sample_datetime
    
    def test_permission_out_optional_updated(self, sample_datetime):
        """Test that updated can be None"""
        permission = PermissionOut(
            id=1,
            name="out_permission",
            created=sample_datetime,
            updated=None
        )
        assert permission.updated is None
    
    def test_permission_out_inherits_base(self, sample_datetime):
        """Test that PermissionOut includes base fields"""
        permission = PermissionOut(
            id=1,
            name="inheritance_test",
            description="test description",
            created=sample_datetime,
            updated=sample_datetime
        )
        assert permission.description == "test description"
    
    def test_permission_out_from_attributes(self, sample_datetime):
        """Test the from_attributes configuration"""
        class DBModel:
            def __init__(self):
                self.id = 1
                self.name = "db_model"
                self.description = "from db"
                self.created = sample_datetime
                self.updated = sample_datetime
        
        db_instance = DBModel()
        permission = PermissionOut.model_validate(db_instance)
        
        assert permission.id == 1
        assert permission.name == "db_model"
        assert permission.description == "from db"
        assert permission.created == sample_datetime