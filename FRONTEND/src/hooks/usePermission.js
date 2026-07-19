import { usePermissionContext } from '../context/PermissionContext.jsx';

/**
 * Hook for permission-based UI gating.
 *
 * @returns {{
 *   hasPermission: (perm: string) => boolean,
 *   hasAnyPermission: (perms: string[]) => boolean,
 *   hasAllPermissions: (perms: string[]) => boolean,
 *   permissions: Set<string>,
 *   isLoading: boolean,
 * }}
 */
export function usePermission() {
  return usePermissionContext();
}
