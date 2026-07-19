import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { permissionsApi } from '../api/permissions.js';
import { STALE_TIME } from '../utils/constants.js';

const PERMS_KEY = 'permissions';

export function usePermissions(params = {}) {
  return useQuery({
    queryKey: [PERMS_KEY, 'list', params],
    queryFn: () => permissionsApi.getAllPermissions(params),
    staleTime: STALE_TIME.LONG,
  });
}

export function usePermissionById(id) {
  return useQuery({
    queryKey: [PERMS_KEY, id],
    queryFn: () => permissionsApi.getPermissionById(id),
    enabled: !!id,
    staleTime: STALE_TIME.LONG,
  });
}

export function usePermissionRoles(permissionId) {
  return useQuery({
    queryKey: [PERMS_KEY, permissionId, 'roles'],
    queryFn: () => permissionsApi.getRoles(permissionId),
    enabled: !!permissionId,
    staleTime: STALE_TIME.MEDIUM,
  });
}

export function useCreatePermission() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: permissionsApi.createPermission,
    onSuccess: () => qc.invalidateQueries({ queryKey: [PERMS_KEY, 'list'] }),
  });
}

export function useUpdatePermission() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) => permissionsApi.updatePermission(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: [PERMS_KEY, id] });
      qc.invalidateQueries({ queryKey: [PERMS_KEY, 'list'] });
    },
  });
}

export function useDeletePermission() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: permissionsApi.deletePermission,
    onSuccess: () => qc.invalidateQueries({ queryKey: [PERMS_KEY, 'list'] }),
  });
}

export function useAssignPermissionToRoleFromPerm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ permissionId, ...data }) => permissionsApi.assignToRole(permissionId, data),
    onSuccess: (_, { permissionId }) =>
      qc.invalidateQueries({ queryKey: [PERMS_KEY, permissionId, 'roles'] }),
  });
}

export function useRemovePermissionFromRoleFromPerm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ permissionId, roleId }) => permissionsApi.removeFromRole(permissionId, roleId),
    onSuccess: (_, { permissionId }) =>
      qc.invalidateQueries({ queryKey: [PERMS_KEY, permissionId, 'roles'] }),
  });
}
