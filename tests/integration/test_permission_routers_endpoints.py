import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.database.permission import Permission

class TestPermissionRouter:
    def test_create_permission_success(self, client: TestClient, test_token: str):
        # Get URL by route name
        url = app.url_path_for("create_permission")
        
        response = client.post(
            url,
            json={
                "name": "create_post",
                "description": "Can create new posts"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()
        assert response.json()["name"] == "create_post"

    def test_create_duplicate_permission_fails(self, client: TestClient, test_token: str):
        # First create
        url = app.url_path_for("create_permission")
        client.post(
            url,
            json={
                "name": "edit_post",
                "description": "Can edit posts"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        
        # Try duplicate
        response = client.post(
            url,
            json={
                "name": "edit_post",  # Duplicate name
                "description": "Different description"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_get_permission_by_id(self, client: TestClient, test_token: str):
        # First create
        create_url = app.url_path_for("create_permission")
        create_res = client.post(
            create_url,
            json={
                "name": "delete_post",
                "description": "Can delete posts"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        perm_id = create_res.json()["id"]
        
        # Now get
        get_url = app.url_path_for("get_permission", id=perm_id)
        response = client.get(
            get_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == perm_id
        assert response.json()["name"] == "delete_post"

    def test_get_nonexistent_permission(self, client: TestClient, test_token: str):
        url = app.url_path_for("get_permission", id=999999)
        response = client.get(
            url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_permission(self, client: TestClient, test_token: str):
        # Create first
        create_url = app.url_path_for("create_permission")
        create_res = client.post(
            create_url,
            json={
                "name": "view_post",
                "description": "Original description"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        perm_id = create_res.json()["id"]
        
        # Update
        update_url = app.url_path_for("update_permission", id=perm_id)
        response = client.put(
            update_url,
            json={"description": "Updated description"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "Updated description"
        assert response.json()["name"] == "view_post"  # Name unchanged

    def test_delete_permission(self, client: TestClient, test_token: str):
        # Create first
        create_url = app.url_path_for("create_permission")
        create_res = client.post(
            create_url,
            json={
                "name": "publish_post",
                "description": "Can publish posts"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        perm_id = create_res.json()["id"]
        
        # Delete
        delete_url = app.url_path_for("delete_permission", id=perm_id)
        response = client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["message"] == "Permission deleted"
        
        # Verify deleted
        get_url = app.url_path_for("get_permission", id=perm_id)
        get_response = client.get(
            get_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_all_permissions(self, client: TestClient, test_token: str):
        # Create test data
        create_url = app.url_path_for("create_permission")
        for i in range(1, 4):
            client.post(
                create_url,
                json={
                    "name": f"perm_{i}",
                    "description": f"Permission {i}"
                },
                headers={"Authorization": f"Bearer {test_token}"}
            )
        
        # Get all
        list_url = app.url_path_for("get_all_permissions")
        response = client.get(
            list_url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 3  # May have other permissions
        assert any(p["name"] == "perm_1" for p in response.json())