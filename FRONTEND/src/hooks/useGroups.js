import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { groupsApi } from '../api/groups.js';
import { STALE_TIME } from '../utils/constants.js';

const GROUPS_KEY = 'groups';

export function useGroups(params = {}) {
  return useQuery({
    queryKey: [GROUPS_KEY, 'list', params],
    queryFn: () => groupsApi.getAllGroups(params),
    staleTime: STALE_TIME.MEDIUM,
  });
}

export function useGroup(id) {
  return useQuery({
    queryKey: [GROUPS_KEY, id],
    queryFn: () => groupsApi.getGroupById(id),
    enabled: !!id,
    staleTime: STALE_TIME.MEDIUM,
  });
}

export function useGroupUsers(groupId) {
  return useQuery({
    queryKey: [GROUPS_KEY, groupId, 'users'],
    queryFn: () => groupsApi.getUsers(groupId),
    enabled: !!groupId,
    staleTime: STALE_TIME.SHORT,
  });
}

export function useGroupRoles(groupId) {
  return useQuery({
    queryKey: [GROUPS_KEY, groupId, 'roles'],
    queryFn: () => groupsApi.getRoles(groupId),
    enabled: !!groupId,
    staleTime: STALE_TIME.MEDIUM,
  });
}

export function useCreateGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: groupsApi.createGroup,
    onSuccess: () => qc.invalidateQueries({ queryKey: [GROUPS_KEY, 'list'] }),
  });
}

export function useUpdateGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) => groupsApi.updateGroup(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: [GROUPS_KEY, id] });
      qc.invalidateQueries({ queryKey: [GROUPS_KEY, 'list'] });
    },
  });
}

export function useDeleteGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: groupsApi.deleteGroup,
    onSuccess: () => qc.invalidateQueries({ queryKey: [GROUPS_KEY, 'list'] }),
  });
}

export function useAddUserToGroupFromGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ groupId, ...data }) => groupsApi.addUser(groupId, data),
    onSuccess: (_, { groupId }) =>
      qc.invalidateQueries({ queryKey: [GROUPS_KEY, groupId, 'users'] }),
  });
}

export function useRemoveUserFromGroupFromGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ groupId, userId }) => groupsApi.removeUser(groupId, userId),
    onSuccess: (_, { groupId }) =>
      qc.invalidateQueries({ queryKey: [GROUPS_KEY, groupId, 'users'] }),
  });
}

export function useAssignRoleToGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ groupId, ...data }) => groupsApi.assignRole(groupId, data),
    onSuccess: (_, { groupId }) =>
      qc.invalidateQueries({ queryKey: [GROUPS_KEY, groupId, 'roles'] }),
  });
}

export function useRemoveRoleFromGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ groupId, roleId }) => groupsApi.removeRole(groupId, roleId),
    onSuccess: (_, { groupId }) =>
      qc.invalidateQueries({ queryKey: [GROUPS_KEY, groupId, 'roles'] }),
  });
}
