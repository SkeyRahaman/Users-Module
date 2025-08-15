import pytest
from fastapi import status
from httpx import AsyncClient
from app.main import app
from app.database.models import Permission

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_database", "override_get_db")
class TestPermissionRouter:

    async def test_create_permission_success(self, client: AsyncClient, token: str):
        url = app.url_path_for("create_permission")
        response = await client.post(
            url,
            json={
                "name": "create_post",
                "description": "Can create new posts"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()
        assert response.json()["name"] == "create_post"

    async def test_create_duplicate_permission_fails(self, client: AsyncClient, token: str, test_permission: Permission):
        url = app.url_path_for("create_permission")
        response = await client.post(
            url,
            json={
                "name": test_permission.name,  # duplicate name from fixture
                "description": "Different description"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    async def test_get_permission_by_id(self, client: AsyncClient, token: str, test_permission: Permission):
        get_url = app.url_path_for("get_permission", id=test_permission.id)
        response = await client.get(
            get_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == test_permission.id
        assert response.json()["name"] == test_permission.name

    async def test_get_nonexistent_permission(self, client: AsyncClient, token: str):
        url = app.url_path_for("get_permission", id=999999)
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_permission(self, client: AsyncClient, token: str, test_permission: Permission):
        update_url = app.url_path_for("update_permission", id=test_permission.id)
        response = await client.put(
            update_url,
            json={"description": "Updated description"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "Updated description"
        assert response.json()["name"] == test_permission.name  # Name unchanged

    async def test_delete_permission(self, client: AsyncClient, token: str, test_permission: Permission):
        delete_url = app.url_path_for("delete_permission", id=test_permission.id)
        response = await client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["message"] == "Permission deleted"

        get_url = app.url_path_for("get_permission", id=test_permission.id)
        get_response = await client.get(
            get_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_all_permissions(self, client: AsyncClient, token: str):
        create_url = app.url_path_for("create_permission")
        for i in range(1, 4):
            await client.post(
                create_url,
                json={
                    "name": f"perm_{i}",
                    "description": f"Permission {i}"
                },
                headers={"Authorization": f"Bearer {token}"}
            )

        list_url = app.url_path_for("get_all_permissions")
        response = await client.get(
            list_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 3
        assert any(p["name"] == "perm_1" for p in response.json())
