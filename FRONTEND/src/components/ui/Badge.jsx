// Badge: coloured pill labels
export function Badge({ children, variant = 'gray', dot = false }) {
  return (
    <span className={`badge badge-${variant}`}>
      {dot && <span className="status-dot" />}
      {children}
    </span>
  );
}

// StatusBadge: convenience wrapper for user is_active / is_verified
export function StatusBadge({ active, label }) {
  if (active) return <Badge variant="success" dot>{label ?? 'Active'}</Badge>;
  return <Badge variant="danger" dot>{label ?? 'Inactive'}</Badge>;
}

// VerifiedBadge
export function VerifiedBadge({ verified }) {
  if (verified) return <Badge variant="info">Verified</Badge>;
  return <Badge variant="warning">Unverified</Badge>;
}
