import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app
from app.database.models import Role

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_database", "override_get_db")
class TestRoleRouter:

    async def test_create_role_success(self, client: AsyncClient, token: str):
        url = app.url_path_for("create_role")
        response = await client.post(
            url,
            json={
                "name": "admin",
                "description": "Administrator role"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()
        assert response.json()["name"] == "admin"

    async def test_create_duplicate_role_fails(self, client: AsyncClient, token: str, test_role: Role):
        url = app.url_path_for("create_role")
        response = await client.post(
            url,
            json={
                "name": test_role.name,  # duplicate name from fixture
                "description": "Different description"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    async def test_get_role_by_id(self, client: AsyncClient, token: str, test_role: Role):
        get_url = app.url_path_for("get_role", id=test_role.id)
        response = await client.get(
            get_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == test_role.id
        assert response.json()["name"] == test_role.name

    async def test_get_nonexistent_role(self, client: AsyncClient, token: str):
        url = app.url_path_for("get_role", id=999999)
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_role(self, client: AsyncClient, token: str, test_role: Role):
        update_url = app.url_path_for("update_role", id=test_role.id)
        response = await client.put(
            update_url,
            json={"description": "Updated description"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "Updated description"
        assert response.json()["name"] == test_role.name  # Name unchanged

    async def test_delete_role(self, client: AsyncClient, token: str, test_role: Role):
        delete_url = app.url_path_for("delete_role", id=test_role.id)
        response = await client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["message"] == "Role deleted"

        get_url = app.url_path_for("get_role", id=test_role.id)
        get_response = await client.get(
            get_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_all_roles(self, client: AsyncClient, token: str):
        create_url = app.url_path_for("create_role")
        for i in range(1, 4):
            await client.post(
                create_url,
                json={
                    "name": f"role_{i}",
                    "description": f"Role {i}"
                },
                headers={"Authorization": f"Bearer {token}"}
            )

        list_url = app.url_path_for("get_all_roles")
        response = await client.get(
            list_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 3
        assert any(r["name"] == "role_1" for r in response.json())

    async def test_get_all_roles_pagination(self, client: AsyncClient, token: str):
        create_url = app.url_path_for("create_role")
        for i in range(1, 21):
            await client.post(
                create_url,
                json={
                    "name": f"paged_role_{i}",
                    "description": f"Role {i}"
                },
                headers={"Authorization": f"Bearer {token}"}
            )

        list_url = app.url_path_for("get_all_roles")
        response = await client.get(
            list_url,
            params={"skip": 5, "limit": 5},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

    async def test_get_all_roles_sorting(self, client: AsyncClient, token: str):
        create_url = app.url_path_for("create_role")
        await client.post(
            create_url,
            json={"name": "beta", "description": "Beta role"},
            headers={"Authorization": f"Bearer {token}"}
        )
        await client.post(
            create_url,
            json={"name": "alpha", "description": "Alpha role"},
            headers={"Authorization": f"Bearer {token}"}
        )

        list_url = app.url_path_for("get_all_roles")
        response = await client.get(
            list_url,
            params={"sort_by": "name", "sort_order": "asc"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        names = [r["name"] for r in response.json()]
        assert names.index("alpha") < names.index("beta")

    async def test_assign_role_to_user_success(self, client: AsyncClient, admin_token: str, test_user: dict, test_role: dict):
        url = app.url_path_for("assign_role_to_user", role_id=test_role.id)
        payload = {"user_id": test_user.id}
        response = await client.post(url, json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 201
        assert "Role assigned to user" in response.json().get("message", "")

    async def test_assign_role_to_user_failure(self, client: AsyncClient, admin_token: str, test_user: dict, test_role: dict):
        url = app.url_path_for("assign_role_to_user", role_id=test_role.id)
        payload = {"user_id": test_user.id}
        response = await client.post(url, json=payload, headers={"Authorization": f"Bearer invalid_token"})
        assert response.status_code != status.HTTP_200_OK

    async def test_remove_role_from_user_success(self, client: AsyncClient, admin_token: str, test_user_role):
        test_user, test_role = test_user_role
        url = app.url_path_for("remove_role_from_user", user_id=test_user.id)
        payload = {"role_id":test_role.id}
        response = await client.post(url, params=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "Role removed from user" in response.json().get("message", "")

    async def test_remove_role_from_user_failure(self, client: AsyncClient, admin_token: str, test_user: dict, test_role: dict):
        url = app.url_path_for("remove_role_from_user", user_id=test_user.id)
        payload = {"role_id":test_role.id}
        response = await client.post(url, params=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code != status.HTTP_202_ACCEPTED

    async def test_assign_role_to_group_success(self, client: AsyncClient, admin_token: str, test_group: dict, test_role: dict):
        url = app.url_path_for("assign_role_to_group", role_id=test_role.id)
        payload = {"group_id": test_group.id}
        response = await client.post(url, json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_201_CREATED
        assert "Role assigned to group" in response.json().get("message", "")

    async def test_assign_role_to_group_failure(self, client: AsyncClient, admin_token: str, test_group: dict, test_role: dict):
        url = app.url_path_for("assign_role_to_group", role_id=test_role.id)
        payload = {"group_id": test_group.id}
        response = await client.post(url, json=payload, headers={"Authorization": f"Bearer invalid_token"})
        assert response.status_code != status.HTTP_201_CREATED

    async def test_remove_role_from_group_success(self, client: AsyncClient, admin_token: str, test_group_role):
        test_group, test_role = test_group_role
        url = app.url_path_for("remove_role_from_group", role_id=test_role.id)
        payload = {"group_id": test_group.id}
        response = await client.post(url, params=payload ,headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "Role removed from group" in response.json().get("message", "")

    async def test_remove_role_from_group_failure(self, client: AsyncClient, admin_token: str, test_group: dict, test_role: dict):
        url = app.url_path_for("remove_role_from_group", role_id=test_role.id)
        payload = {"group_id": test_group.id}
        response = await client.post(url, params=payload ,headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code != status.HTTP_202_ACCEPTED

    async def test_get_users_for_role_success(self, client: AsyncClient, admin_token: str, test_role: dict):
        url = app.url_path_for("get_users_for_role", role_id=test_role.id)
        response = await client.get(url, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_get_users_for_role_failure(self, client: AsyncClient, admin_token: str):
        url = app.url_path_for("get_users_for_role", role_id=999999)
        response = await client.get(url, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_groups_for_role_success(self, client: AsyncClient, admin_token: str, test_role: dict):
        url = app.url_path_for("get_groups_for_role", role_id=test_role.id)
        response = await client.get(url, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_get_groups_for_role_failure(self, client: AsyncClient, admin_token: str):
        url = app.url_path_for("get_groups_for_role", role_id=999999)
        response = await client.get(url, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_add_permission_to_role_success(self, client: AsyncClient, admin_token: str, test_role: dict, test_permission: dict):
        url = app.url_path_for("add_permission_to_role", role_id=test_role.id)
        payload = {"permission_id": test_permission.id}
        response = await client.post(url, json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_201_CREATED
        assert "Permission added to role" in response.json().get("message", "")

    async def test_add_permission_to_role_failure(self, client: AsyncClient, admin_token: str, test_role: dict, test_permission: dict):
        url = app.url_path_for("add_permission_to_role", role_id=test_role.id)
        payload = {"permission_id": test_permission.id}
        response = await client.post(url, json=payload, headers={"Authorization": f"Bearer invalid_token"})
        assert response.status_code != status.HTTP_201_CREATED

    async def test_remove_permission_from_role_success(self, client: AsyncClient, admin_token: str, test_role_permission):
        test_role, test_permission = test_role_permission
        url = app.url_path_for("remove_permission_from_role", role_id=test_role.id)
        payload = {"permission_id": test_permission.id}
        response = await client.post(url, params=payload ,headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "Permission removed from role" in response.json().get("message", "")

    async def test_remove_permission_from_role_failure(self, client: AsyncClient, admin_token: str, test_role: dict, test_permission: dict):
        url = app.url_path_for("remove_permission_from_role", role_id=test_role.id)
        payload = {"permission_id": test_permission.id}
        response = await client.post(url, params=payload ,headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code != status.HTTP_202_ACCEPTED

    async def test_get_permissions_for_role_success(self, client: AsyncClient, admin_token: str, test_role: dict):
        url = app.url_path_for("get_permissions_for_role", role_id=test_role.id)
        response = await client.get(url, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_get_permissions_for_role_failure(self, client: AsyncClient, admin_token: str):
        url = app.url_path_for("get_permissions_for_role", role_id=999999)
        response = await client.get(url, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_404_NOT_FOUND
