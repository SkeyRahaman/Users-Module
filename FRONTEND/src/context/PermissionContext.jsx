import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { rolesApi } from '../api/roles.js';
import { usersApi } from '../api/users.js';
import { useAuth } from './AuthContext.jsx';

const PermissionContext = createContext(null);

export function PermissionProvider({ children }) {
  const { user, isAuthenticated } = useAuth();
  // Start as `true` only when we have an authenticated user to resolve — this
  // prevents a false "loaded" flash before the first resolve runs.
  const [permissions, setPermissions] = useState(new Set());
  const [isLoading, setIsLoading] = useState(true);

  const resolvePermissions = useCallback(async () => {
    if (!isAuthenticated) {
      // Not logged in — no permissions, not loading
      setPermissions(new Set());
      setIsLoading(false);
      return;
    }

    if (!user) {
      // Auth is set but user object not yet hydrated — keep loading
      return;
    }

    setIsLoading(true);
    try {
      // 1. Get user's direct roles + group roles
      let roles = [];
      try {
        roles = await usersApi.getUserRoles(user.id);
      } catch {
        // Permission denied or network error — graceful fallback to empty roles
        roles = [];
      }

      if (!roles || roles.length === 0) {
        setPermissions(new Set());
      } else {
        // 2. For each role, fetch permissions
        const permissionSets = await Promise.allSettled(
          roles.map((role) => rolesApi.getPermissions(role.id))
        );

        const allPerms = new Set();
        permissionSets.forEach((result) => {
          if (result.status === 'fulfilled' && Array.isArray(result.value)) {
            result.value.forEach((p) => allPerms.add(p.name));
          }
        });

        setPermissions(allPerms);
      }
    } catch {
      // Entire resolution failed — safe fallback to empty permissions
      setPermissions(new Set());
    } finally {
      setIsLoading(false);
    }
  }, [user, isAuthenticated]);

  useEffect(() => {
    resolvePermissions();
  }, [resolvePermissions]);

  const hasPermission = useCallback(
    (perm) => permissions.has(perm),
    [permissions]
  );

  const hasAnyPermission = useCallback(
    (perms) => perms.some((p) => permissions.has(p)),
    [permissions]
  );

  const hasAllPermissions = useCallback(
    (perms) => perms.every((p) => permissions.has(p)),
    [permissions]
  );

  const value = {
    permissions,
    isLoading,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    refresh: resolvePermissions,
  };

  return (
    <PermissionContext.Provider value={value}>
      {children}
    </PermissionContext.Provider>
  );
}

export function usePermissionContext() {
  const ctx = useContext(PermissionContext);
  if (!ctx) throw new Error('usePermissionContext must be used within <PermissionProvider>');
  return ctx;
}
