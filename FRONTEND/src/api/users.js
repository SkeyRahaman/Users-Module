import apiClient from './client.js';

export const usersApi = {
  /** POST /users/ — Register a new user (public) */
  createUser: async (data) => {
    const response = await apiClient.post('/users/', data);
    return response.data;
  },

  /** GET /users/me */
  getMe: async () => {
    const response = await apiClient.get('/users/me');
    return response.data;
  },

  /** PUT /users/me */
  updateMe: async (data) => {
    const response = await apiClient.put('/users/me', data);
    return response.data;
  },

  /** DELETE /users/me */
  deleteMe: async () => {
    const response = await apiClient.delete('/users/me');
    return response.data;
  },

  /** GET /users/get_all_users — requires search_user */
  getAllUsers: async ({ page = 1, limit = 20, sort = 'created', order = 'desc', status, role, group, search } = {}) => {
    const params = { page, limit, sort, order };
    if (status !== undefined) params.status = status;
    if (role) params.role = role;
    if (group) params.group = group;
    if (search) params.search = search;
    const response = await apiClient.get('/users/get_all_users', { params });
    return response.data;
  },

  /** GET /users/{id} — requires search_user */
  getUserById: async (id) => {
    const response = await apiClient.get(`/users/${id}`);
    return response.data;
  },

  /** POST /users/{id}/activate — requires activate_user */
  activateUser: async (userId) => {
    const response = await apiClient.post(`/users/${userId}/activate`);
    return response.data;
  },

  /** POST /users/{id}/deactivate — requires deactivate_user */
  deactivateUser: async (userId, reason) => {
    const params = reason ? { reason } : {};
    const response = await apiClient.post(`/users/${userId}/deactivate`, null, { params });
    return response.data;
  },

  /** GET /users/{id}/activity_logs — requires view_audit_logs */
  getActivityLogs: async (userId, { limit = 50, offset = 0 } = {}) => {
    const response = await apiClient.get(`/users/${userId}/activity_logs`, {
      params: { limit, offset },
    });
    return response.data;
  },

  /** POST /users/{id}/add_to_group — requires assign_user_to_group */
  addToGroup: async (userId, { group_id, valid_from, valid_until } = {}) => {
    const response = await apiClient.post(`/users/${userId}/add_to_group`, {
      group_id,
      valid_from: valid_from || null,
      valid_until: valid_until || null,
    });
    return response.data;
  },

  /** POST /users/{id}/remove_from_group — requires remove_user_from_group */
  removeFromGroup: async (userId, groupId) => {
    const response = await apiClient.post(`/users/${userId}/remove_from_group`, null, {
      params: { group_id: groupId },
    });
    return response.data;
  },

  /** GET /users/{id}/groups — requires remove_user_from_group */
  getUserGroups: async (userId) => {
    const response = await apiClient.get(`/users/${userId}/groups`);
    return response.data;
  },

  /** POST /users/{id}/assign_role — requires assign_role_to_user */
  assignRole: async (userId, { role_id, valid_from, valid_until } = {}) => {
    const response = await apiClient.post(`/users/${userId}/assign_role`, {
      role_id,
      valid_from: valid_from || null,
      valid_until: valid_until || null,
    });
    return response.data;
  },

  /** POST /users/{id}/remove_role — requires assign_role_to_user */
  removeRole: async (userId, roleId) => {
    const response = await apiClient.post(`/users/${userId}/remove_role`, null, {
      params: { role_id: roleId },
    });
    return response.data;
  },

  /** GET /users/{id}/roles — requires assign_role_to_user */
  getUserRoles: async (userId) => {
    const response = await apiClient.get(`/users/${userId}/roles`);
    return response.data;
  },
};
