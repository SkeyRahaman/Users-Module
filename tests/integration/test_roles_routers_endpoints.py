import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

class TestRoleRouter:
    def test_create_role_success(self, client: TestClient, test_token: str):
        # Get URL by route name
        url = app.url_path_for("create_role")
        
        response = client.post(
            url,
            json={
                "name": "admin",
                "description": "Administrator role"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()
        assert response.json()["name"] == "admin"

    def test_create_duplicate_role_fails(self, client: TestClient, test_token: str):
        # First create
        url = app.url_path_for("create_role")
        client.post(
            url,
            json={
                "name": "editor",
                "description": "Editor role"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        
        # Try duplicate
        response = client.post(
            url,
            json={
                "name": "editor",  # Duplicate name
                "description": "Different description"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_get_role_by_id(self, client: TestClient, test_token: str):
        # First create
        create_url = app.url_path_for("create_role")
        create_res = client.post(
            create_url,
            json={
                "name": "viewer",
                "description": "Viewer role"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        role_id = create_res.json()["id"]
        
        # Now get
        get_url = app.url_path_for("get_role", id=role_id)
        response = client.get(
            get_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == role_id
        assert response.json()["name"] == "viewer"

    def test_get_nonexistent_role(self, client: TestClient, test_token: str):
        url = app.url_path_for("get_role", id=999999)
        response = client.get(
            url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_role(self, client: TestClient, test_token: str):
        # Create first
        create_url = app.url_path_for("create_role")
        create_res = client.post(
            create_url,
            json={
                "name": "moderator",
                "description": "Original description"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        role_id = create_res.json()["id"]
        
        # Update
        update_url = app.url_path_for("update_role", id=role_id)
        response = client.put(
            update_url,
            json={"description": "Updated description"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "Updated description"
        assert response.json()["name"] == "moderator"  # Name unchanged

    def test_delete_role(self, client: TestClient, test_token: str):
        # Create first
        create_url = app.url_path_for("create_role")
        create_res = client.post(
            create_url,
            json={
                "name": "guest",
                "description": "Guest role"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        role_id = create_res.json()["id"]
        
        # Delete
        delete_url = app.url_path_for("delete_role", id=role_id)
        response = client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["message"] == "Role deleted"
        
        # Verify deleted
        get_url = app.url_path_for("get_role", id=role_id)
        get_response = client.get(
            get_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_all_roles(self, client: TestClient, test_token: str):
        # Create test data
        create_url = app.url_path_for("create_role")
        for i in range(1, 4):
            client.post(
                create_url,
                json={
                    "name": f"role_{i}",
                    "description": f"Role {i}"
                },
                headers={"Authorization": f"Bearer {test_token}"}
            )
        
        # Get all
        list_url = app.url_path_for("get_all_roles")
        response = client.get(
            list_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 3  # May have other roles
        assert any(r["name"] == "role_1" for r in response.json())

    def test_get_all_roles_pagination(self, client: TestClient, test_token: str):
        # Create test data
        create_url = app.url_path_for("create_role")
        for i in range(1, 21):
            client.post(
                create_url,
                json={
                    "name": f"paged_role_{i}",
                    "description": f"Role {i}"
                },
                headers={"Authorization": f"Bearer {test_token}"}
            )
        
        # Get paginated results
        list_url = app.url_path_for("get_all_roles")
        response = client.get(
            list_url,
            params={"skip": 5, "limit": 5},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

    def test_get_all_roles_sorting(self, client: TestClient, test_token: str):
        # Create test data with different names
        create_url = app.url_path_for("create_role")
        client.post(
            create_url,
            json={"name": "beta", "description": "Beta role"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        client.post(
            create_url,
            json={"name": "alpha", "description": "Alpha role"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        
        # Get sorted results
        list_url = app.url_path_for("get_all_roles")
        response = client.get(
            list_url,
            params={"sort_by": "name", "sort_order": "asc"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        names = [r["name"] for r in response.json()]
        assert names.index("alpha") < names.index("beta")
