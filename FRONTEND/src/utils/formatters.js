import { formatDistanceToNow, format, parseISO, isValid } from 'date-fns';

/**
 * Format a date string to a human-readable relative time (e.g. "2 hours ago")
 */
export function timeAgo(dateStr) {
  if (!dateStr) return '—';
  try {
    const date = typeof dateStr === 'string' ? parseISO(dateStr) : dateStr;
    if (!isValid(date)) return '—';
    return formatDistanceToNow(date, { addSuffix: true });
  } catch {
    return '—';
  }
}

/**
 * Format a date string to a readable absolute date (e.g. "Jul 18, 2026")
 */
export function formatDate(dateStr, fmt = 'MMM d, yyyy') {
  if (!dateStr) return '—';
  try {
    const date = typeof dateStr === 'string' ? parseISO(dateStr) : dateStr;
    if (!isValid(date)) return '—';
    return format(date, fmt);
  } catch {
    return '—';
  }
}

/**
 * Format a date to full datetime (e.g. "Jul 18, 2026 at 9:30 PM")
 */
export function formatDateTime(dateStr) {
  return formatDate(dateStr, "MMM d, yyyy 'at' h:mm a");
}

/**
 * Get user's display name from a UserOut object
 */
export function getUserDisplayName(user) {
  if (!user) return 'Unknown';
  const parts = [user.firstname, user.middlename, user.lastname].filter(Boolean);
  return parts.join(' ');
}

/**
 * Get initials from a user object (for avatars)
 */
export function getUserInitials(user) {
  if (!user) return '?';
  const first = user.firstname?.[0] ?? '';
  const last = user.lastname?.[0] ?? '';
  return (first + last).toUpperCase() || user.username?.[0]?.toUpperCase() || '?';
}

/**
 * Truncate a string to a max length with ellipsis
 */
export function truncate(str, maxLen = 40) {
  if (!str) return '';
  return str.length > maxLen ? str.slice(0, maxLen) + '…' : str;
}

/**
 * Format a number with thousands separators
 */
export function formatNumber(n) {
  if (n === null || n === undefined) return '0';
  return new Intl.NumberFormat().format(n);
}

/**
 * Convert backend sort field name to display label
 */
export function sortFieldLabel(field) {
  const map = {
    created: 'Date Created',
    username: 'Username',
    email: 'Email',
    id: 'ID',
    name: 'Name',
  };
  return map[field] ?? field;
}

/**
 * Get activity log icon type from an event type string
 */
export function getActivityIconType(eventType) {
  if (!eventType) return 'default';
  const type = eventType.toLowerCase();
  if (type.includes('login') || type.includes('auth')) return 'login';
  if (type.includes('creat') || type.includes('register')) return 'create';
  if (type.includes('updat') || type.includes('edit')) return 'update';
  if (type.includes('delet') || type.includes('remov') || type.includes('deactivat')) return 'delete';
  if (type.includes('assign') || type.includes('add') || type.includes('activat')) return 'assign';
  return 'default';
}
