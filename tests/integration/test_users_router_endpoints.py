import uuid
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from app.main import app
from app.database.models import User
from app.config import Config
from app.auth.password_hash import PasswordHasher

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_database", "override_get_db")
class TestUsersRouter:

    async def test_create_user_success(self, client: AsyncClient):
        url = app.url_path_for("create_user")

        response = await client.post(
            url,
            json={
                "firstname":"TestFirst_" + uuid.uuid4().hex[:6],
                "lastname":"TestLast_" + uuid.uuid4().hex[:6],
                "username":"user_" + uuid.uuid4().hex[:8],
                "email":f"user_{uuid.uuid4().hex[:8]}@example.com",
                "password": PasswordHasher.get_password_hash(Config.TEST_USER['password']),
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()

    async def test_get_current_user(self, client: AsyncClient, test_user: User, token: str):
        url = app.url_path_for("get_me")

        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == test_user.username

    async def test_update_current_user(self, client: AsyncClient, test_user: User, token: str):
        url = app.url_path_for("put_me")

        response = await client.put(
            url,
            json={"email": "updated@example.com"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "updated@example.com"

    async def test_delete_current_user(self, client: AsyncClient, test_user: User, token: str):
        url = app.url_path_for("delete_me")

        response = await client.delete(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["Message"] == "User Deleted."

    async def test_get_user_by_id(self, client: AsyncClient, test_user: User, admin_token: str):
        url = app.url_path_for("get_by_id", id=test_user.id)

        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == test_user.id

    # Error cases
    async def test_create_user_duplicate(self, client: AsyncClient, test_user: User):
        url = app.url_path_for("create_user")

        response = await client.post(
            url,
            json={
                "firstname": "Test",
                "lastname": "User",
                "username": test_user.username,
                "email": test_user.email,
                "password": "secure123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_nonexistent_user(self, client: AsyncClient, admin_token: str):
        url = app.url_path_for("get_by_id", id=999999)

        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_all_users(self, client: AsyncClient, admin_token: str, test_user: User
    ):
        url = app.url_path_for("get_all_users")
        params = {
            "page": 1,
            "limit": 10,
            "sort": "created",
            "order": "desc",
            "status": True,
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert "page" in data and data["page"] == 1
        assert "limit" in data and data["limit"] == 10
        assert "total" in data and isinstance(data["total"], int)
        assert "users" in data and isinstance(data["users"], list)
        assert any(user["id"] == test_user.id or user["username"] == test_user.username for user in data["users"])

    async def test_get_all_users_no_auth(self, client):
        url = app.url_path_for("get_all_users")
        response = await client.get(url, params={"page": 1, "limit": 10})
        assert response.status_code in (401, 403)

    async def test_get_all_users_invalid_token(self, client):
        url = app.url_path_for("get_all_users")
        response = await client.get(url, headers={"Authorization": "Bearer invalidtoken"})
        assert response.status_code == 401

    async def test_get_all_users_invalid_page_limit(self, client, admin_token):
        url = app.url_path_for("get_all_users")
        params = {"page": "abc", "limit": -1}
        response = await client.get(url, headers={"Authorization": f"Bearer {admin_token}"}, params=params)
        assert response.status_code in (400, 422)

    async def test_get_all_users_permission_denied(self, client, token):
        url = app.url_path_for("get_all_users")
        response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_get_all_users_empty_result(self, client, admin_token: str):
        url = app.url_path_for("get_all_users")
        params = {"search": "nonexistentusername"}
        response = await client.get(url, headers={"Authorization": f"Bearer {admin_token}"}, params=params)
        assert response.status_code == 200
        assert response.json()["users"] == []

    async def test_activate_user_success(self, db_session: AsyncSession, client: AsyncClient, admin_token: str, test_user: User):
        test_user.is_active = False
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)

        url = app.url_path_for("activate_user", user_id=test_user.id)
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(url, headers=headers)
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert data["status"] == "active"
        assert "updated_at" in data


    async def test_activate_user_failure_unauthorized(self, client: AsyncClient, test_user: User):
        url = app.url_path_for("activate_user", user_id=test_user.id)
        response = await client.post(url)  # no auth header
        assert response.status_code in (401, 403)


    async def test_activate_user_failure_not_found(self, client: AsyncClient, admin_token: str):
        url = app.url_path_for("activate_user", user_id=99999)  # non-existent user id
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(url, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    async def test_deactivate_user_success(self, client: AsyncClient, admin_token: str, test_user: User):
        url = app.url_path_for("deactivate_user", user_id=test_user.id)
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(url, headers=headers)
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert data["status"] == "inactive"
        assert "updated_at" in data


    async def test_deactivate_user_failure_unauthorized(self, client: AsyncClient, test_user: User):
        url = app.url_path_for("deactivate_user", user_id=test_user.id)
        response = await client.post(url)  # no auth header
        assert response.status_code in (401, 403)


    async def test_deactivate_user_failure_not_found(self, client: AsyncClient, admin_token: str):
        url = app.url_path_for("deactivate_user", user_id=99999)  # non-existent user id
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(url, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_user_activity_logs_success(self, client: AsyncClient, test_user: User, admin_token: str):
        user_id = test_user.id
        mocked_logs = [{"action": "login", "timestamp": "2025-08-27T22:00:00Z"}]
        mocked_total = 1

        with patch(
            "app.database.services.user_service.UserService.get_users_activity_logs",
            new_callable=AsyncMock,
            return_value=(mocked_logs, mocked_total)
        ):
            url = app.url_path_for("get_user_activity_logs", user_id=user_id)
            response = await client.get(url, headers={"Authorization": f"Bearer {admin_token}"})

            assert response.status_code == status.HTTP_200_OK
            assert response.json() == {
                "user_id": user_id,
                "total": mocked_total,
                "limit": 50,
                "offset": 0,
                "activities": mocked_logs,
            }

    @pytest.mark.asyncio
    async def test_get_user_activity_logs_not_found(self, client: AsyncClient, test_user: User, admin_token: str):
        user_id = test_user.id

        with patch(
            "app.database.services.user_service.UserService.get_users_activity_logs",
            new_callable=AsyncMock,
            return_value=(None, 0)
        ):
            url = app.url_path_for("get_user_activity_logs", user_id=user_id)
            response = await client.get(url, headers={"Authorization": f"Bearer {admin_token}"})

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "User not found or no activity logs available."}

    async def test_add_user_to_group(self, client, admin_token, test_user, test_group):
        url = app.url_path_for("add_user_to_group", user_id=test_user.id)
        resp = await client.post(
            url,
            json={"group_id": test_group.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["user_id"] == test_user.id
        assert data["group_id"] == test_group.id

    async def test_add_user_to_group_fail_notfound(self, client, admin_token, test_user):
        # Assuming group_id 999999 does not exist
        url = app.url_path_for("add_user_to_group", user_id=test_user.id)
        resp = await client.post(
            url,
            json={"group_id": 999999},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_remove_user_from_group(self, client, admin_token, test_user, test_group):
        # First add, then remove
        add_url = app.url_path_for("add_user_to_group", user_id=test_user.id)
        await client.post(
            add_url,
            json={"group_id": test_group.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        remove_url = app.url_path_for("remove_user_from_group", user_id=test_user.id)
        resp = await client.post(
            remove_url,
            params={"group_id": test_group.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_202_ACCEPTED
        assert "User removed from group successfully" in resp.json()["message"]

    async def test_remove_user_from_group_fail(self, client, admin_token, test_user):
        url = app.url_path_for("remove_user_from_group", user_id=test_user.id)
        resp = await client.post(
            url, 
            params={"group_id": 999999},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_groups_of_user(self, client, admin_token, test_user, test_group):
        # Add group first
        add_url = app.url_path_for("add_user_to_group", user_id=test_user.id)
        await client.post(
            add_url,
            json={"group_id": test_group.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        url = app.url_path_for("get_groups_of_user", user_id=test_user.id)
        resp = await client.get(
            url,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK
        groups = resp.json()
        assert any(g["id"] == test_group.id for g in groups)

    async def test_get_groups_of_user_notfound(self, client, admin_token):
        url = app.url_path_for("get_groups_of_user", user_id=999999)
        resp = await client.get(
            url,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_assign_role_to_user(self, client, admin_token, test_user, test_role):
        url = app.url_path_for("assigne_role_to_user", user_id=test_user.id)
        resp = await client.post(
            url,
            json={"role_id": test_role.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert "Role assigned to user successfully" in resp.json()["message"]

    async def test_assign_role_to_user_fail(self, client, admin_token, test_user):
        url = app.url_path_for("assigne_role_to_user", user_id=test_user.id)
        resp = await client.post(
            url,
            json={"role_id": 999999},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_remove_role_from_user(self, client, admin_token, test_user, test_role):
        # Assign role first
        assign_url = app.url_path_for("assigne_role_to_user", user_id=test_user.id)
        await client.post(
            assign_url,
            json={"role_id": test_role.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        url = app.url_path_for("remove_role_from_user", user_id=test_user.id)
        resp = await client.post(
            url,
            params={"role_id": test_role.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_202_ACCEPTED
        assert "Role removed from user successfully" in resp.json()["message"]

    async def test_remove_role_from_user_fail(self, client, admin_token, test_user):
        url = app.url_path_for("remove_role_from_user", user_id=test_user.id)
        resp = await client.post(
            url,
            params={"role_id": 999999},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_roles_of_user(self, client, admin_token, test_user, test_role):
        # Assign role first
        assign_url = app.url_path_for("assigne_role_to_user", user_id=test_user.id)
        await client.post(
            assign_url,
            json={"role_id": test_role.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        url = app.url_path_for("get_roles_of_user", user_id=test_user.id)
        resp = await client.get(
            url,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK
        roles = resp.json()
        assert any(r["id"] == test_role.id for r in roles)

    async def test_get_roles_of_user_notfound(self, client, admin_token):
        url = app.url_path_for("get_roles_of_user", user_id=999999)
        resp = await client.get(
            url,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
