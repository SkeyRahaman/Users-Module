import apiClient from './client.js';

export const groupsApi = {
  /** POST /groups/ */
  createGroup: async (data) => {
    const response = await apiClient.post('/groups/', data);
    return response.data;
  },

  /** GET /groups/ */
  getAllGroups: async ({ skip = 0, limit = 50, sort_by = 'created', sort_order = 'desc' } = {}) => {
    const response = await apiClient.get('/groups/', { params: { skip, limit, sort_by, sort_order } });
    return response.data;
  },

  /** GET /groups/{id} */
  getGroupById: async (id) => {
    const response = await apiClient.get(`/groups/${id}`);
    return response.data;
  },

  /** GET /groups/name/{name} */
  getGroupByName: async (name) => {
    const response = await apiClient.get(`/groups/name/${encodeURIComponent(name)}`);
    return response.data;
  },

  /** PUT /groups/{id} */
  updateGroup: async (id, data) => {
    const response = await apiClient.put(`/groups/${id}`, data);
    return response.data;
  },

  /** DELETE /groups/{id} */
  deleteGroup: async (id) => {
    const response = await apiClient.delete(`/groups/${id}`);
    return response.data;
  },

  /** POST /groups/{id}/add_user — requires assign_user_to_group */
  addUser: async (groupId, { user_id, valid_from, valid_until } = {}) => {
    const response = await apiClient.post(`/groups/${groupId}/add_user`, {
      user_id,
      valid_from: valid_from || null,
      valid_until: valid_until || null,
    });
    return response.data;
  },

  /** POST /groups/{id}/remove_user — requires remove_user_from_group */
  removeUser: async (groupId, userId) => {
    const response = await apiClient.post(`/groups/${groupId}/remove_user`, null, {
      params: { user_id: userId },
    });
    return response.data;
  },

  /** GET /groups/{id}/users — requires remove_user_from_group */
  getUsers: async (groupId) => {
    const response = await apiClient.get(`/groups/${groupId}/users`);
    return response.data;
  },

  /** POST /groups/{id}/assigne_role — requires remove_user_from_group */
  assignRole: async (groupId, { role_id, valid_from, valid_until } = {}) => {
    const response = await apiClient.post(`/groups/${groupId}/assigne_role`, {
      role_id,
      valid_from: valid_from || null,
      valid_until: valid_until || null,
    });
    return response.data;
  },

  /** POST /groups/{id}/remove_role — requires remove_user_from_group */
  removeRole: async (groupId, roleId) => {
    const response = await apiClient.post(`/groups/${groupId}/remove_role`, null, {
      params: { role_id: roleId },
    });
    return response.data;
  },

  /** GET /groups/{id}/roles — requires remove_user_from_group */
  getRoles: async (groupId) => {
    const response = await apiClient.get(`/groups/${groupId}/roles`);
    return response.data;
  },
};
