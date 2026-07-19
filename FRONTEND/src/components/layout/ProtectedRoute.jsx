import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth.js';
import { usePermission } from '../../hooks/usePermission.js';

export default function ProtectedRoute({ children, requiredPermission }) {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { hasPermission, isLoading: permLoading } = usePermission();
  const location = useLocation();

  // Wait for auth to initialise (restoring session from storage)
  if (authLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', gap: '1rem', background: 'var(--bg-primary)' }}>
        <div className="btn-spinner" style={{ width: 40, height: 40, borderTopColor: 'var(--accent)' }} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Loading session...</p>
      </div>
    );
  }

  // Not authenticated — go to login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Authenticated — wait for permissions to resolve before checking gates.
  // Only block if a specific permission is required (don't block public-for-all-auth routes like /dashboard).
  if (requiredPermission && permLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', gap: '1rem', background: 'var(--bg-primary)' }}>
        <div className="btn-spinner" style={{ width: 40, height: 40, borderTopColor: 'var(--accent)' }} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Resolving permissions...</p>
      </div>
    );
  }

  // Permission gate — redirect to unauthorized if user lacks required permission
  if (requiredPermission && !permLoading && !hasPermission(requiredPermission)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}
