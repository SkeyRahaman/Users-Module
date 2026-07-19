import { usePermission } from '../../hooks/usePermission.js';

/**
 * Permission gate component.
 * Renders children only if the current user has the required permission(s).
 *
 * @param {string|string[]} permission  - Required permission string(s)
 * @param {'all'|'any'} mode            - 'all' (default) or 'any'
 * @param {React.ReactNode} fallback    - What to render when permission is missing (default: null)
 */
export default function Can({ permission, mode = 'all', fallback = null, children }) {
  const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermission();

  const perms = Array.isArray(permission) ? permission : [permission];

  const allowed =
    perms.length === 0
      ? true
      : mode === 'any'
      ? hasAnyPermission(perms)
      : hasAllPermissions(perms);

  return allowed ? children : fallback;
}
