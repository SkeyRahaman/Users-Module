---
name: Get All Users in a Group
about: Request a new API endpoint to fetch all users belonging to a specific group.
title: '[Feature]: Get All Users in a Group Endpoint'
labels: enhancement, api
assignees: ''
---

# Feature Request: Get All Users in a Group Endpoint

## Summary
We need a new API endpoint to retrieve **all users associated with a given group**. This will allow client applications and admin dashboards to easily query members of a particular group without retrieving all users and filtering manually on the client side.

## Proposed Endpoint
**Path:**  
`GET /groups/{group_id}/users`

**Description:**  
Fetch all users belonging to the specified group.

## Request
- **Path Parameter:**
  - `group_id` (UUID or int, depending on schema): The ID of the group.

- **Query Parameters (optional):**
  - `limit` (int, default 20) – pagination support.
  - `offset` (int, default 0) – pagination support.
  - `active_only` (bool, default false) – filter only active users if needed.

## Response
- **200 OK**
```
{
  "group_id": "uuid-or-int",
  "group_name": "Admins",
  "users": [
    {
      "id": "uuid-or-int",
      "email": "user1@example.com",
      "full_name": "User One",
      "is_active": true,
      "created_at": "2025-09-28T10:00:00Z"
    },
    {
      "id": "uuid-or-int",
      "email": "user2@example.com",
      "full_name": "User Two",
      "is_active": true,
      "created_at": "2025-09-27T15:30:00Z"
    }
  ],
  "total": 2
}
```

- **404 Not Found**
```
{
  "detail": "Group not found"
}
```

- **403 Forbidden**
```
{
  "detail": "Not authorized to access this group"
}
```

## Acceptance Criteria
- [ ] A new endpoint `GET /groups/{group_id}/users` is available.
- [ ] Endpoint supports pagination (`limit`, `offset`).
- [ ] Endpoint returns user objects consistent with the `UserOut` schema.
- [ ] Unauthorized users cannot access groups they don’t belong to (RBAC/permission check).
- [ ] Proper error handling for edge cases (e.g., group not found).

## Additional Notes
- Aligns with existing `Users` and `Groups` module patterns.
- Will help admins manage group memberships more effectively.
- Potential future extension: filter by role within a group.
