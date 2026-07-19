import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '../api/users.js';
import { STALE_TIME } from '../utils/constants.js';

const USERS_KEY = 'users';

export function useUsers(filters = {}) {
  return useQuery({
    queryKey: [USERS_KEY, 'list', filters],
    queryFn: () => usersApi.getAllUsers(filters),
    staleTime: STALE_TIME.SHORT,
  });
}

export function useUser(id) {
  return useQuery({
    queryKey: [USERS_KEY, id],
    queryFn: () => usersApi.getUserById(id),
    enabled: !!id,
    staleTime: STALE_TIME.SHORT,
  });
}

export function useMe() {
  return useQuery({
    queryKey: [USERS_KEY, 'me'],
    queryFn: usersApi.getMe,
    staleTime: STALE_TIME.SHORT,
  });
}

export function useUserRoles(userId) {
  return useQuery({
    queryKey: [USERS_KEY, userId, 'roles'],
    queryFn: () => usersApi.getUserRoles(userId),
    enabled: !!userId,
    staleTime: STALE_TIME.MEDIUM,
  });
}

export function useUserGroups(userId) {
  return useQuery({
    queryKey: [USERS_KEY, userId, 'groups'],
    queryFn: () => usersApi.getUserGroups(userId),
    enabled: !!userId,
    staleTime: STALE_TIME.MEDIUM,
  });
}

export function useActivityLogs(userId, paginationOpts = {}) {
  return useQuery({
    queryKey: [USERS_KEY, userId, 'activity', paginationOpts],
    queryFn: () => usersApi.getActivityLogs(userId, paginationOpts),
    enabled: !!userId,
    staleTime: STALE_TIME.SHORT,
  });
}

// Mutations
export function useUpdateMe() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: usersApi.updateMe,
    onSuccess: () => qc.invalidateQueries({ queryKey: [USERS_KEY, 'me'] }),
  });
}

export function useActivateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (userId) => usersApi.activateUser(userId),
    onSuccess: (_, userId) => {
      qc.invalidateQueries({ queryKey: [USERS_KEY, userId] });
      qc.invalidateQueries({ queryKey: [USERS_KEY, 'list'] });
    },
  });
}

export function useDeactivateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, reason }) => usersApi.deactivateUser(userId, reason),
    onSuccess: (_, { userId }) => {
      qc.invalidateQueries({ queryKey: [USERS_KEY, userId] });
      qc.invalidateQueries({ queryKey: [USERS_KEY, 'list'] });
    },
  });
}

export function useAssignUserRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, ...data }) => usersApi.assignRole(userId, data),
    onSuccess: (_, { userId }) =>
      qc.invalidateQueries({ queryKey: [USERS_KEY, userId, 'roles'] }),
  });
}

export function useRemoveUserRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, roleId }) => usersApi.removeRole(userId, roleId),
    onSuccess: (_, { userId }) =>
      qc.invalidateQueries({ queryKey: [USERS_KEY, userId, 'roles'] }),
  });
}

export function useAddUserToGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, ...data }) => usersApi.addToGroup(userId, data),
    onSuccess: (_, { userId }) =>
      qc.invalidateQueries({ queryKey: [USERS_KEY, userId, 'groups'] }),
  });
}

export function useRemoveUserFromGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, groupId }) => usersApi.removeFromGroup(userId, groupId),
    onSuccess: (_, { userId }) =>
      qc.invalidateQueries({ queryKey: [USERS_KEY, userId, 'groups'] }),
  });
}
