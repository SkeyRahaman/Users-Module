import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.group import GroupBase, GroupCreate, GroupUpdate, GroupOut

class TestGroupBase:
    """Test cases for GroupBase model"""
    
    def test_valid_group_base(self):
        """Test valid GroupBase creation"""
        group = GroupBase(
            name="developers",
            description="Engineering team"
        )
        assert group.name == "developers"
        assert group.description == "Engineering team"
    
    def test_minimal_group_base(self):
        """Test GroupBase with minimal required fields"""
        group = GroupBase(name="marketing")
        assert group.name == "marketing"
        assert group.description is None
    
    def test_invalid_group_base_missing_name(self):
        """Test GroupBase with missing required field"""
        with pytest.raises(ValidationError):
            GroupBase(description="Missing group name")

class TestGroupCreate:
    """Test cases for GroupCreate model"""
    
    def test_group_create_inheritance(self):
        """Test that GroupCreate inherits from GroupBase"""
        group = GroupCreate(
            name="designers",
            description="UX/UI team"
        )
        assert isinstance(group, GroupBase)
        assert group.name == "designers"
    
    def test_group_create_identical_to_base(self):
        """Test that GroupCreate has same fields as GroupBase"""
        base_fields = GroupBase.model_fields
        create_fields = GroupCreate.model_fields
        assert base_fields.keys() == create_fields.keys()

class TestGroupUpdate:
    """Test cases for GroupUpdate model"""
    
    def test_group_update_all_optional(self):
        """Test that all fields in GroupUpdate are optional"""
        group = GroupUpdate()
        assert group.name is None
        assert group.description is None
    
    def test_partial_group_update(self):
        """Test updating just one field"""
        group = GroupUpdate(name="new_group_name")
        assert group.name == "new_group_name"
        assert group.description is None
        
        group = GroupUpdate(description="new_description")
        assert group.name is None
        assert group.description == "new_description"
    
    def test_full_group_update(self):
        """Test updating all fields"""
        group = GroupUpdate(
            name="updated_group",
            description="updated description"
        )
        assert group.name == "updated_group"
        assert group.description == "updated description"

class TestGroupOut:
    """Test cases for GroupOut model"""
    
    @pytest.fixture
    def sample_datetime(self):
        return datetime(2023, 1, 1, 12, 0, 0)
    
    def test_group_out_required_fields(self, sample_datetime):
        """Test required fields in GroupOut"""
        group = GroupOut(
            id=1,
            name="qa_team",
            created=sample_datetime,
            updated=sample_datetime,
            is_deleted=False
        )
        assert group.id == 1
        assert group.name == "qa_team"
        assert group.created == sample_datetime
        assert group.updated == sample_datetime
        assert group.is_deleted is False
    
    def test_group_out_optional_fields(self, sample_datetime):
        """Test optional fields in GroupOut"""
        group = GroupOut(
            id=1,
            name="devops",
            created=sample_datetime,
            updated=None,
            is_deleted=None
        )
        assert group.updated is None
        assert group.is_deleted is None
    
    def test_group_out_inherits_base(self, sample_datetime):
        """Test that GroupOut includes base fields"""
        group = GroupOut(
            id=1,
            name="product",
            description="Product management",
            created=sample_datetime,
            updated=sample_datetime,
            is_deleted=False
        )
        assert group.description == "Product management"
    
    def test_group_out_from_attributes(self, sample_datetime):
        """Test the from_attributes configuration"""
        class DBModel:
            def __init__(self):
                self.id = 1
                self.name = "db_group"
                self.description = "from database"
                self.created = sample_datetime
                self.updated = sample_datetime
                self.is_deleted = True
        
        db_instance = DBModel()
        group = GroupOut.model_validate(db_instance)
        
        assert group.id == 1
        assert group.name == "db_group"
        assert group.description == "from database"
        assert group.created == sample_datetime
        assert group.is_deleted is True