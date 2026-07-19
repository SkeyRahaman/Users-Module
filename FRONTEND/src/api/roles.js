import apiClient from './client.js';

export const rolesApi = {
  /** POST /roles/ */
  createRole: async (data) => {
    const response = await apiClient.post('/roles/', data);
    return response.data;
  },

  /** GET /roles/ */
  getAllRoles: async ({ skip = 0, limit = 100, sort_by = 'created', sort_order = 'desc' } = {}) => {
    const response = await apiClient.get('/roles/', { params: { skip, limit, sort_by, sort_order } });
    return response.data;
  },

  /** GET /roles/{id} */
  getRoleById: async (id) => {
    const response = await apiClient.get(`/roles/${id}`);
    return response.data;
  },

  /** PUT /roles/{id} */
  updateRole: async (id, data) => {
    const response = await apiClient.put(`/roles/${id}`, data);
    return response.data;
  },

  /** DELETE /roles/{id} */
  deleteRole: async (id) => {
    const response = await apiClient.delete(`/roles/${id}`);
    return response.data;
  },

  /** POST /roles/{id}/assign_user — requires assign_role_to_user */
  assignUser: async (roleId, { user_id, valid_from, valid_until } = {}) => {
    const response = await apiClient.post(`/roles/${roleId}/assign_user`, {
      user_id,
      valid_from: valid_from || null,
      valid_until: valid_until || null,
    });
    return response.data;
  },

  /** POST /roles/{id}/remove_user — requires assign_role_to_user */
  removeUser: async (roleId, userId) => {
    const response = await apiClient.post(`/roles/${roleId}/remove_user`, null, {
      params: { user_id: userId },
    });
    return response.data;
  },

  /** GET /roles/{id}/users — requires view_roles */
  getUsers: async (roleId) => {
    const response = await apiClient.get(`/roles/${roleId}/users`);
    return response.data;
  },

  /** POST /roles/{id}/assign_group — requires assign_role_to_user */
  assignGroup: async (roleId, { group_id, valid_from, valid_until } = {}) => {
    const response = await apiClient.post(`/roles/${roleId}/assign_group`, {
      group_id,
      valid_from: valid_from || null,
      valid_until: valid_until || null,
    });
    return response.data;
  },

  /** POST /roles/{id}/remove_group — requires assign_role_to_user */
  removeGroup: async (roleId, groupId) => {
    const response = await apiClient.post(`/roles/${roleId}/remove_group`, null, {
      params: { group_id: groupId },
    });
    return response.data;
  },

  /** GET /roles/{id}/groups — requires view_roles */
  getGroups: async (roleId) => {
    const response = await apiClient.get(`/roles/${roleId}/groups`);
    return response.data;
  },

  /** POST /roles/{id}/assigne_permission — requires assign_role_to_user */
  assignPermission: async (roleId, { permission_id, valid_from, valid_until } = {}) => {
    const response = await apiClient.post(`/roles/${roleId}/assigne_permission`, {
      permission_id,
      valid_from: valid_from || null,
      valid_until: valid_until || null,
    });
    return response.data;
  },

  /** POST /roles/{id}/remove_permission — requires assign_role_to_user */
  removePermission: async (roleId, permissionId) => {
    const response = await apiClient.post(`/roles/${roleId}/remove_permission`, null, {
      params: { permission_id: permissionId },
    });
    return response.data;
  },

  /** GET /roles/{id}/permissions — requires view_roles */
  getPermissions: async (roleId) => {
    const response = await apiClient.get(`/roles/${roleId}/permissions`);
    return response.data;
  },
};
