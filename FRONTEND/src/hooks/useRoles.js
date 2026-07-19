import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { rolesApi } from '../api/roles.js';
import { STALE_TIME } from '../utils/constants.js';

const ROLES_KEY = 'roles';

export function useRoles(params = {}) {
  return useQuery({
    queryKey: [ROLES_KEY, 'list', params],
    queryFn: () => rolesApi.getAllRoles(params),
    staleTime: STALE_TIME.MEDIUM,
  });
}

export function useRole(id) {
  return useQuery({
    queryKey: [ROLES_KEY, id],
    queryFn: () => rolesApi.getRoleById(id),
    enabled: !!id,
    staleTime: STALE_TIME.MEDIUM,
  });
}

export function useRoleUsers(roleId) {
  return useQuery({
    queryKey: [ROLES_KEY, roleId, 'users'],
    queryFn: () => rolesApi.getUsers(roleId),
    enabled: !!roleId,
    staleTime: STALE_TIME.SHORT,
  });
}

export function useRoleGroups(roleId) {
  return useQuery({
    queryKey: [ROLES_KEY, roleId, 'groups'],
    queryFn: () => rolesApi.getGroups(roleId),
    enabled: !!roleId,
    staleTime: STALE_TIME.MEDIUM,
  });
}

export function useRolePermissions(roleId) {
  return useQuery({
    queryKey: [ROLES_KEY, roleId, 'permissions'],
    queryFn: () => rolesApi.getPermissions(roleId),
    enabled: !!roleId,
    staleTime: STALE_TIME.LONG,
  });
}

export function useCreateRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: rolesApi.createRole,
    onSuccess: () => qc.invalidateQueries({ queryKey: [ROLES_KEY, 'list'] }),
  });
}

export function useUpdateRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) => rolesApi.updateRole(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: [ROLES_KEY, id] });
      qc.invalidateQueries({ queryKey: [ROLES_KEY, 'list'] });
    },
  });
}

export function useDeleteRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: rolesApi.deleteRole,
    onSuccess: () => qc.invalidateQueries({ queryKey: [ROLES_KEY, 'list'] }),
  });
}

export function useAssignUserToRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ roleId, ...data }) => rolesApi.assignUser(roleId, data),
    onSuccess: (_, { roleId }) =>
      qc.invalidateQueries({ queryKey: [ROLES_KEY, roleId, 'users'] }),
  });
}

export function useRemoveUserFromRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ roleId, userId }) => rolesApi.removeUser(roleId, userId),
    onSuccess: (_, { roleId }) =>
      qc.invalidateQueries({ queryKey: [ROLES_KEY, roleId, 'users'] }),
  });
}

export function useAssignGroupToRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ roleId, ...data }) => rolesApi.assignGroup(roleId, data),
    onSuccess: (_, { roleId }) =>
      qc.invalidateQueries({ queryKey: [ROLES_KEY, roleId, 'groups'] }),
  });
}

export function useRemoveGroupFromRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ roleId, groupId }) => rolesApi.removeGroup(roleId, groupId),
    onSuccess: (_, { roleId }) =>
      qc.invalidateQueries({ queryKey: [ROLES_KEY, roleId, 'groups'] }),
  });
}

export function useAssignPermissionToRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ roleId, ...data }) => rolesApi.assignPermission(roleId, data),
    onSuccess: (_, { roleId }) =>
      qc.invalidateQueries({ queryKey: [ROLES_KEY, roleId, 'permissions'] }),
  });
}

export function useRemovePermissionFromRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ roleId, permissionId }) => rolesApi.removePermission(roleId, permissionId),
    onSuccess: (_, { roleId }) =>
      qc.invalidateQueries({ queryKey: [ROLES_KEY, roleId, 'permissions'] }),
  });
}
