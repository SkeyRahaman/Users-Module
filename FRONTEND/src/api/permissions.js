import apiClient from './client.js';

export const permissionsApi = {
  /** POST /permissions/ */
  createPermission: async (data) => {
    const response = await apiClient.post('/permissions/', data);
    return response.data;
  },

  /** GET /permissions/ */
  getAllPermissions: async ({ skip = 0, limit = 200, sort_by = 'created', sort_order = 'desc' } = {}) => {
    const response = await apiClient.get('/permissions/', { params: { skip, limit, sort_by, sort_order } });
    return response.data;
  },

  /** GET /permissions/{id} */
  getPermissionById: async (id) => {
    const response = await apiClient.get(`/permissions/${id}`);
    return response.data;
  },

  /** PUT /permissions/{id} */
  updatePermission: async (id, data) => {
    const response = await apiClient.put(`/permissions/${id}`, data);
    return response.data;
  },

  /** DELETE /permissions/{id} */
  deletePermission: async (id) => {
    const response = await apiClient.delete(`/permissions/${id}`);
    return response.data;
  },

  /** POST /permissions/{id}/assigne_roles — requires assign_role_to_user */
  assignToRole: async (permissionId, { role_id, valid_from, valid_until } = {}) => {
    const response = await apiClient.post(`/permissions/${permissionId}/assigne_roles`, {
      role_id,
      valid_from: valid_from || null,
      valid_until: valid_until || null,
    });
    return response.data;
  },

  /** POST /permissions/{id}/remove_roles — requires assign_role_to_user */
  removeFromRole: async (permissionId, roleId) => {
    const response = await apiClient.post(`/permissions/${permissionId}/remove_roles`, null, {
      params: { role_id: roleId },
    });
    return response.data;
  },

  /** GET /permissions/{id}/roles */
  getRoles: async (permissionId) => {
    const response = await apiClient.get(`/permissions/${permissionId}/roles`);
    return response.data;
  },
};

/** GET /health — public */
export const healthApi = {
  check: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};
