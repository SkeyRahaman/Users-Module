import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

class TestGroupRouter:
    def test_create_group_success(self, client: TestClient, test_token: str):
        # Get URL by route name
        url = app.url_path_for("create_group")
        
        response = client.post(
            url,
            json={
                "name": "developers",
                "description": "Development team"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()
        assert response.json()["name"] == "developers"

    def test_create_duplicate_group_fails(self, client: TestClient, test_token: str):
        # First create
        url = app.url_path_for("create_group")
        client.post(
            url,
            json={
                "name": "managers",
                "description": "Management team"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        
        # Try duplicate
        response = client.post(
            url,
            json={
                "name": "managers",  # Duplicate name
                "description": "Different description"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_get_group_by_id(self, client: TestClient, test_token: str):
        # First create
        create_url = app.url_path_for("create_group")
        create_res = client.post(
            create_url,
            json={
                "name": "qa",
                "description": "Quality Assurance"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        group_id = create_res.json()["id"]
        
        # Now get
        get_url = app.url_path_for("get_group", id=group_id)
        response = client.get(
            get_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == group_id
        assert response.json()["name"] == "qa"

    def test_get_nonexistent_group(self, client: TestClient, test_token: str):
        url = app.url_path_for("get_group", id=999999)
        response = client.get(
            url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_group(self, client: TestClient, test_token: str):
        # Create first
        create_url = app.url_path_for("create_group")
        create_res = client.post(
            create_url,
            json={
                "name": "designers",
                "description": "Original description"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        group_id = create_res.json()["id"]
        
        # Update
        update_url = app.url_path_for("update_group", id=group_id)
        response = client.put(
            update_url,
            json={"description": "Updated description"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "Updated description"
        assert response.json()["name"] == "designers"  # Name unchanged

    def test_delete_group(self, client: TestClient, test_token: str):
        # Create first
        create_url = app.url_path_for("create_group")
        create_res = client.post(
            create_url,
            json={
                "name": "marketing",
                "description": "Marketing team"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        group_id = create_res.json()["id"]
        
        # Delete
        delete_url = app.url_path_for("delete_group", id=group_id)
        response = client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["message"] == "Group deleted"
        
        # Verify deleted
        get_url = app.url_path_for("get_group", id=group_id)
        get_response = client.get(
            get_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_all_groups(self, client: TestClient, test_token: str):
        # Create test data
        create_url = app.url_path_for("create_group")
        for i in range(1, 4):
            client.post(
                create_url,
                json={
                    "name": f"group_{i}",
                    "description": f"Group {i}"
                },
                headers={"Authorization": f"Bearer {test_token}"}
            )
        
        # Get all
        list_url = app.url_path_for("get_all_groups")
        response = client.get(
            list_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 3  # May have other groups
        assert any(g["name"] == "group_1" for g in response.json())

    def test_get_group_by_name(self, client: TestClient, test_token: str):
        # First create
        create_url = app.url_path_for("create_group")
        client.post(
            create_url,
            json={
                "name": "finance",
                "description": "Finance department"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        
        # Get by name
        get_url = app.url_path_for("get_group_by_name", name="finance")
        response = client.get(
            get_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "finance"

    def test_get_group_by_name_not_found(self, client: TestClient, test_token: str):
        url = app.url_path_for("get_group_by_name", name="nonexistent")
        response = client.get(
            url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_all_groups_pagination(self, client: TestClient, test_token: str):
        # Create test data
        create_url = app.url_path_for("create_group")
        for i in range(1, 21):
            client.post(
                create_url,
                json={
                    "name": f"paged_group_{i}",
                    "description": f"Group {i}"
                },
                headers={"Authorization": f"Bearer {test_token}"}
            )
        
        # Get paginated results
        list_url = app.url_path_for("get_all_groups")
        response = client.get(
            list_url,
            params={"skip": 5, "limit": 5},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

    def test_get_all_groups_sorting(self, client: TestClient, test_token: str):
        # Create test data with different names
        create_url = app.url_path_for("create_group")
        client.post(
            create_url,
            json={"name": "beta_group", "description": "Beta group"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        client.post(
            create_url,
            json={"name": "alpha_group", "description": "Alpha group"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        
        # Get sorted results
        list_url = app.url_path_for("get_all_groups")
        response = client.get(
            list_url,
            params={"sort_by": "name", "sort_order": "asc"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        names = [g["name"] for g in response.json()]
        assert names.index("alpha_group") < names.index("beta_group")
