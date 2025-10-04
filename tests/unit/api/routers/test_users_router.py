import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User

from app.api.routers import users as users_router
from app.schemas.user import UserCreate, UserOut, UserUpdate, UsersResponse
from app.database.services.user_service import UserService
from app.database.services.users_roles_services import UserRoleService

@pytest.mark.asyncio
class TestUserRouter:
    async def test_create_user_success(self, mock_db):
        test_data = UserCreate(
            firstname="test",
            lastname="user",
            username="newuser",
            email="new@example.com",
            password="secure123"
        )
        # Create a mock user to return from UserService.create_user
        mock_user = MagicMock()
        mock_user.id = 42
        mock_user.username = "newuser"
        mock_user.email = "new@example.com"
        mock_user.is_deleted = False

        # Simulate assign_user_role returning True (success)
        with patch.object(UserService, "create_user", new_callable=AsyncMock, return_value=mock_user) as create_user_mock, \
             patch.object(UserRoleService, "assigne_user_role", new_callable=AsyncMock, return_value=True) as assign_role_mock:
            response = await users_router.create_user(test_data, mock_db)
            assert response.username == "newuser"
            assert response.email == "new@example.com"
            create_user_mock.assert_awaited_once_with(mock_db, test_data)
            assign_role_mock.assert_awaited_once_with(mock_db, mock_user.id, 1, created_by=mock_user.id)

    # 🔸 GET /users/me
    async def test_get_me(self, mock_current_user):
        response = await users_router.get_me(mock_current_user)
        assert response == mock_current_user

    # 🔸 PUT /users/me
    async def test_update_me(self, mock_db, mock_current_user):
        update_data = UserUpdate(email="updated@example.com")
        updated_user = MagicMock()
        updated_user.email = "updated@example.com"

        with patch.object(UserService, "update_user", new_callable=AsyncMock, return_value=updated_user):
            response = await users_router.update_me(update_data, mock_db, mock_current_user)
            assert response.email == "updated@example.com"
            UserService.update_user.assert_awaited_once_with(mock_db, mock_current_user.id, update_data)

    # 🔸 DELETE /users/me
    async def test_delete_me(self, mock_db, mock_current_user):
        with patch.object(UserService, "delete_user", new_callable=AsyncMock) as mock_delete:
            response = await users_router.delete_me(mock_db, mock_current_user)
            assert response == {"Message": "User Deleted."}
            mock_delete.assert_awaited_once_with(mock_db, mock_current_user.id)

    # 🔸 GET /users/{id}
    async def test_get_user_by_id(self, mock_db, mock_current_user):
        test_user = MagicMock()
        test_user.id = 2

        with patch.object(UserService, "get_user_by_id", new_callable=AsyncMock, return_value=test_user):
            response = await users_router.get_user_by_id(2, mock_db, mock_current_user)
            assert response.id == 2
            UserService.get_user_by_id.assert_awaited_once_with(mock_db, 2)

    # ---- Error Cases ----
    async def test_create_user_duplicate_email(self, mock_db):
        test_data = UserCreate(
            firstname="nrw",
            lastname="usesr",
            username="newuser",
            email="duplicate@example.com",
            password="secure123"
        )
        with patch.object(
            UserService,
            "create_user",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=400, detail="Email already exists")
        ), pytest.raises(HTTPException) as exc_info:
            await users_router.create_user(test_data, mock_db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_nonexistent_user(self, mock_db, mock_current_user):
        with patch.object(
            UserService,
            "get_user_by_id",
            new_callable=AsyncMock,
            return_value=None
        ):
            with pytest.raises(HTTPException) as exc_info:
                await users_router.get_user_by_id(999, mock_db, mock_current_user)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_all_users(self, mocker):
        mock_session = AsyncMock(spec=AsyncSession)
        dummy_user = User(
            id=1,
            firstname="John",
            middlename=None,
            lastname="Doe",
            username="johndoe",
            email="john@example.com",
            password="hashed_password",
            is_active=True,
            is_verified=True,
            is_deleted=False,
            user_roles=[],
            user_groups=[],
            created="2025-08-21 15:24:55",
            updated="2025-08-21 15:24:55"
        )
        mock_service = mocker.patch("app.database.services.user_service.UserService.get_all_users", return_value=(1, [dummy_user]))
        response = await users_router.get_all_users(
            page=1,
            limit=50,
            sort="created",
            order="desc",
            status=True,
            role=None,
            group=None,
            search=None,
            session=mock_session
        )
        mock_service.assert_called_once_with(
            db=mock_session,
            page=1,
            limit=50,
            sort_by="created",
            sort_order="desc",
            status=True,
            role=None,
            group=None,
            search=None
        )
        assert isinstance(response, UsersResponse)
        assert response.page == 1
        assert response.limit == 50
        assert response.total == 1
        assert isinstance(response.users, list)
        assert len(response.users) == 1
        assert isinstance(response.users[0], UserOut)
        assert response.users[0].username == dummy_user.username

    async def test_activate_user_success(self, mock_db):
        user_id = 123
        with patch.object(
            UserService,
            "activate_user",
            new_callable=AsyncMock,
            return_value=True
        ):
            response = await users_router.activate_user(user_id, mock_db)
            assert response["status"] == "active"
            assert "updated_at" in response


    async def test_activate_user_failure_raises(self, mock_db):
        user_id = 123
        with patch.object(
            UserService,
            "activate_user",
            new_callable=AsyncMock,
            return_value=False
        ), pytest.raises(HTTPException) as exc_info:
            await users_router.activate_user(user_id, mock_db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Activation failed" in exc_info.value.detail


    async def test_deactivate_user_success(self, mock_db):
        user_id = 123
        reason = "No longer active"
        with patch.object(
            UserService,
            "deactivate_user",
            new_callable=AsyncMock,
            return_value=True
        ):
            response = await users_router.deactivate_user(user_id, reason, mock_db)
            assert response["status"] == "inactive"
            assert "updated_at" in response


    async def test_deactivate_user_failure_raises(self, mock_db):
        user_id = 123
        reason = None
        with patch.object(
            UserService,
            "deactivate_user",
            new_callable=AsyncMock,
            return_value=False
        ), pytest.raises(HTTPException) as exc_info:
            await users_router.deactivate_user(user_id, reason, mock_db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Deactivation failed" in exc_info.value.detail

    async def test_get_user_activity_logs_success(self, mock_db):
        user_id = 1
        mocked_logs = [{"action": "login", "timestamp": "2025-08-27T22:00:00Z"}]
        mocked_total = 1

        with patch.object(UserService, "get_users_activity_logs", new_callable=AsyncMock, return_value=(mocked_logs, mocked_total)):
            # Call function with default limit and offset
            response = await users_router.get_user_activity_logs(user_id=user_id, db=mock_db, limit=50, offset=0)
            print(response)
            assert response["activities"] == mocked_logs
            assert response["total"] == mocked_total
            assert response["limit"] == 50  # default limit
            assert response["offset"] == 0  # default offset
            UserService.get_users_activity_logs.assert_awaited_once_with(user_id=user_id, db=mock_db, limit=50, offset=0)

    async def test_get_user_activity_logs_not_found(self, mock_db):
        user_id = 2

        with patch.object(UserService, "get_users_activity_logs", new_callable=AsyncMock, return_value=(None, 0)):
            with pytest.raises(HTTPException) as exc_info:
                await users_router.get_user_activity_logs(user_id=user_id, db=mock_db, limit=50, offset=0)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert exc_info.value.detail == "User not found or no activity logs available."
            UserService.get_users_activity_logs.assert_awaited_once_with(user_id=user_id, db=mock_db, limit=50, offset=0)
    # 🔸 POST /users/{user_id}/add_to_group
    async def test_add_user_to_group_success(self, mock_db, mock_current_user):
        user_id = 10
        group_id = 20
        mock_request_data = MagicMock()
        mock_request_data.group_id = group_id
        with patch.object(
            users_router.UserGroupService, "assign_user_group",
            new_callable=AsyncMock, return_value=True
        ) as mock_assign:
            response = await users_router.add_user_to_group(
                user_id=user_id,
                request_data=mock_request_data,
                db=mock_db,
                current_user=mock_current_user
            )
            assert response["message"] == "User added to group successfully"
            assert response["group_id"] == group_id
            assert response["user_id"] == user_id
            mock_assign.assert_awaited_once_with(
                db=mock_db, user_id=user_id, group_id=group_id, created_by=mock_current_user.id
            )

    async def test_add_user_to_group_failure(self, mock_db, mock_current_user):
        user_id = 10
        group_id = 20
        mock_request_data = MagicMock()
        mock_request_data.group_id = group_id
        with patch.object(
            users_router.UserGroupService, "assign_user_group",
            new_callable=AsyncMock, return_value=False
        ), pytest.raises(HTTPException) as exc_info:
            await users_router.add_user_to_group(
                user_id=user_id,
                request_data=mock_request_data,
                db=mock_db,
                current_user=mock_current_user
            )
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Failed to add user to group" in exc_info.value.detail

    # 🔸 POST /users/{user_id}/remove_from_group
    async def test_remove_user_from_group_success(self, mock_db, mock_current_user):
        user_id = 10
        group_id = 20
        with patch.object(
            users_router.UserGroupService, "remove_user_group",
            new_callable=AsyncMock, return_value=True
        ) as mock_remove:
            response = await users_router.remove_user_from_group(
                user_id=user_id,
                group_id=group_id,
                db=mock_db,
                _ =  mock_current_user
            )
            assert response["message"] == "User removed from group successfully"
            mock_remove.assert_awaited_once_with(
                db=mock_db, group_id=group_id, user_id=user_id
            )

    async def test_remove_user_from_group_failure(self, mock_db, mock_current_user):
        user_id = 10
        group_id = 20
        with patch.object(
            users_router.UserGroupService, "remove_user_group",
            new_callable=AsyncMock, return_value=False
        ), pytest.raises(HTTPException) as exc_info:
            await users_router.remove_user_from_group(
                user_id=user_id,
                group_id=group_id,
                db=mock_db,
                _ =  mock_current_user
            )
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Failed to remove user from group" in exc_info.value.detail
            
    async def test_assign_role_to_user_success(self, mock_db, mock_current_user):
        user_id = 10
        role_id = 5
        mockrequest = MagicMock()
        mockrequest.role_id = role_id

        with patch('app.database.services.UserRoleService.assigne_user_role', new_callable=AsyncMock) as mock_assign:
            mock_assign.return_value = True

            response = await users_router.assigne_role_to_user(
                user_id=user_id,
                request_data=mockrequest,
                db=mock_db,
                current_user=mock_current_user,
            )

            assert response['message'] == "Role assigned to user successfully"
            mock_assign.assert_awaited_once_with(
                db=mock_db, user_id=user_id, role_id=role_id, created_by=mock_current_user.id
                )

    async def test_assign_role_to_user_failure(self, mock_db, mock_current_user):
        user_id = 10
        role_id = 5
        mockrequest = MagicMock()
        mockrequest.role_id = role_id

        with patch('app.database.services.UserRoleService.assigne_user_role', new_callable=AsyncMock) as mock_assign:
            mock_assign.return_value = False

            with pytest.raises(HTTPException) as excinfo:
                await users_router.assigne_role_to_user(
                    user_id=user_id,
                    request_data=mockrequest,
                    db=mock_db,
                    current_user=mock_current_user,
                )
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Failed to assign role to user" in excinfo.value.detail

    async def test_remove_role_from_user_success(self, mock_db, mock_current_user):
        user_id = 10
        role_id = 5

        with patch('app.database.services.UserRoleService.remove_user_role', new_callable=AsyncMock) as mock_remove:
            mock_remove.return_value = True

            response = await users_router.remove_role_from_user(
                user_id=user_id,
                role_id=role_id,
                db=mock_db,
                _=mock_current_user,
            )

            assert response['message'] == "Role removed from user successfully"
            mock_remove.assert_awaited_once_with(db=mock_db, user_id=user_id, role_id=role_id)
             
            

    async def test_remove_role_from_user_failure(self, mock_db, mock_current_user):
        user_id = 10
        role_id = 5

        with patch('app.database.services.UserRoleService.remove_user_role', new_callable=AsyncMock) as mock_remove:
            mock_remove.return_value = False

            with pytest.raises(HTTPException) as excinfo:
                await users_router.remove_role_from_user(
                    user_id=user_id,
                    role_id=role_id,
                    db=mock_db,
                    _=mock_current_user,
                )
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Failed to remove role from user" in excinfo.value.detail

    async def test_get_groups_of_user_success(self, mock_db, mock_current_user):
        user_id = 10
        groups = [MagicMock(id=1), MagicMock(id=2)]
        with patch.object(users_router.UserGroupService, "get_all_groups_for_user", new_callable=AsyncMock, return_value=groups) as mock_groups:
            response = await users_router.get_groups_of_user(user_id, mock_db, mock_current_user)
            assert response == groups
            mock_groups.assert_awaited_once_with(db=mock_db, user_id=10)

    async def test_get_groups_of_user_notfound(self, mock_db, mock_current_user):
        user_id = 10
        with patch.object(users_router.UserGroupService, "get_all_groups_for_user", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as excinfo:
                await users_router.get_groups_of_user(user_id, mock_db, mock_current_user)
            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
            assert "User not found or no groups assigned" in excinfo.value.detail

    async def test_get_roles_of_user_success(self, mock_db, mock_current_user):
        user_id = 12
        roles = [MagicMock(id=5), MagicMock(id=6)]
        with patch.object(users_router.UserRoleService, "get_all_roles_for_user", new_callable=AsyncMock, return_value=roles) as mock_roles:
            response = await users_router.get_roles_of_user(user_id, mock_db, mock_current_user)
            assert response == roles
            mock_roles.assert_awaited_once_with(db=mock_db, user_id=12)

    async def test_get_roles_of_user_notfound(self, mock_db, mock_current_user):
        user_id = 12
        with patch.object(users_router.UserRoleService, "get_all_roles_for_user", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as excinfo:
                await users_router.get_roles_of_user(user_id, mock_db, mock_current_user)
            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
            assert "User not found or no roles assigned" in excinfo.value.detail
