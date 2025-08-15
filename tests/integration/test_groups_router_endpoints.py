import pytest
from fastapi import status
from httpx import AsyncClient
from app.main import app
from app.database.models import Group

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_database", "override_get_db")
class TestGroupRouter:

    async def test_create_group_success(self, client: AsyncClient, token: str):
        url = app.url_path_for("create_group")

        response = await client.post(
            url,
            json={
                "name": "developers",
                "description": "Development team"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()
        assert response.json()["name"] == "developers"

    async def test_create_duplicate_group_fails(self, client: AsyncClient, token: str, test_group: Group):
        url = app.url_path_for("create_group")

        response = await client.post(
            url,
            json={
                "name": test_group.name,
                "description": "Different description"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    async def test_get_group_by_id(self, client: AsyncClient, token: str, test_group: Group):
        get_url = app.url_path_for("get_group", id=test_group.id)
        response = await client.get(
            get_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == test_group.id
        assert response.json()["name"] == test_group.name

    async def test_get_nonexistent_group(self, client: AsyncClient, token: str):
        url = app.url_path_for("get_group", id=999999)
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_group(self, client: AsyncClient, token: str):
        create_url = app.url_path_for("create_group")
        create_res = await client.post(
            create_url,
            json={
                "name": "designers",
                "description": "Original description"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        group_id = create_res.json()["id"]

        update_url = app.url_path_for("update_group", id=group_id)
        response = await client.put(
            update_url,
            json={"description": "Updated description"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "Updated description"
        assert response.json()["name"] == "designers"  # Name unchanged

    async def test_delete_group(self, client: AsyncClient, token: str, test_group: Group):
        delete_url = app.url_path_for("delete_group", id=test_group.id)
        response = await client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["message"] == "Group deleted"

        get_url = app.url_path_for("get_group", id=test_group.id)
        get_response = await client.get(
            get_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_all_groups(self, client: AsyncClient, token: str):
        create_url = app.url_path_for("create_group")
        for i in range(1, 4):
            await client.post(
                create_url,
                json={
                    "name": f"group_{i}",
                    "description": f"Group {i}"
                },
                headers={"Authorization": f"Bearer {token}"}
            )

        list_url = app.url_path_for("get_all_groups")
        response = await client.get(
            list_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 3
        assert any(g["name"] == "group_1" for g in response.json())

    async def test_get_group_by_name(self, client: AsyncClient, token: str, test_group: Group):
        get_url = app.url_path_for("get_group_by_name", name=test_group.name)
        response = await client.get(
            get_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == test_group.name

    async def test_get_group_by_name_not_found(self, client: AsyncClient, token: str):
        url = app.url_path_for("get_group_by_name", name="nonexistent")
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_all_groups_pagination(self, client: AsyncClient, token: str):
        create_url = app.url_path_for("create_group")
        for i in range(1, 21):
            await client.post(
                create_url,
                json={
                    "name": f"paged_group_{i}",
                    "description": f"Group {i}"
                },
                headers={"Authorization": f"Bearer {token}"}
            )

        list_url = app.url_path_for("get_all_groups")
        response = await client.get(
            list_url,
            params={"skip": 5, "limit": 5},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

    async def test_get_all_groups_sorting(self, client: AsyncClient, token: str):
        create_url = app.url_path_for("create_group")
        await client.post(
            create_url,
            json={"name": "beta_group", "description": "Beta group"},
            headers={"Authorization": f"Bearer {token}"}
        )
        await client.post(
            create_url,
            json={"name": "alpha_group", "description": "Alpha group"},
            headers={"Authorization": f"Bearer {token}"}
        )

        list_url = app.url_path_for("get_all_groups")
        response = await client.get(
            list_url,
            params={"sort_by": "name", "sort_order": "asc"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        names = [g["name"] for g in response.json()]
        assert names.index("alpha_group") < names.index("beta_group")
