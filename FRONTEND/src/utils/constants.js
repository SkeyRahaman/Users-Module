// Application constants

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Permission string constants — must match backend require_permission() calls exactly
export const PERMISSIONS = {
  SEARCH_USER: 'search_user',
  ACTIVATE_USER: 'activate_user',
  DEACTIVATE_USER: 'deactivate_user',
  VIEW_AUDIT_LOGS: 'view_audit_logs',
  ASSIGN_USER_TO_GROUP: 'assign_user_to_group',
  REMOVE_USER_FROM_GROUP: 'remove_user_from_group',
  ASSIGN_ROLE_TO_USER: 'assign_role_to_user',
  VIEW_ROLES: 'view_roles',
};

// sessionStorage keys
export const SESSION_KEYS = {
  ACCESS_TOKEN: 'um_access_token',
  REFRESH_TOKEN: 'um_refresh_token',
  USER: 'um_user',
};

// BroadcastChannel name
export const AUTH_CHANNEL = 'um_auth_channel';

// Pagination defaults
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 20,
  LIMIT_OPTIONS: [10, 20, 50, 100],
};

// Sort orders
export const SORT_ORDER = {
  ASC: 'asc',
  DESC: 'desc',
};

// Query cache stale times (ms)
export const STALE_TIME = {
  SHORT: 30_000,       // 30s — users list (changes often)
  MEDIUM: 60_000,      // 1m  — groups/roles
  LONG: 300_000,       // 5m  — permissions (rarely changes)
};
