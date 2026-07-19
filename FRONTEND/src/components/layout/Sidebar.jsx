import { useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  FolderLock,
  UserCheck,
  ShieldCheck,
  User,
  ChevronLeft,
  Settings2,
  X
} from 'lucide-react';
import { usePermission } from '../../hooks/usePermission.js';
import { PERMISSIONS } from '../../utils/constants.js';

export default function Sidebar({ isCollapsed, onToggle, isMobileOpen, onMobileClose }) {
  const { hasPermission } = usePermission();

  // Close mobile sidebar when pressing Escape
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isMobileOpen) {
        onMobileClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isMobileOpen, onMobileClose]);

  const handleNavClick = () => {
    // Auto-close sidebar on mobile when a link is clicked
    if (window.innerWidth <= 768) {
      onMobileClose();
    }
  };

  return (
    <aside className={`sidebar ${isMobileOpen ? 'mobile-open' : ''}`}>
      <div className="sidebar-header">
        <div className="logo-container">
          <div className="auth-logo-mark" style={{ width: 36, height: 36, borderRadius: 'var(--radius-sm)' }}>
            <Settings2 size={20} />
          </div>
          <span className="logo-text">AuthConsole</span>
        </div>
        {/* Desktop collapse button */}
        <button
          className="sidebar-collapse-btn sidebar-desktop-toggle"
          onClick={onToggle}
          aria-label="Toggle Sidebar"
        >
          <ChevronLeft size={18} />
        </button>
        {/* Mobile close button */}
        <button
          className="sidebar-collapse-btn sidebar-mobile-close"
          onClick={onMobileClose}
          aria-label="Close Sidebar"
        >
          <X size={18} />
        </button>
      </div>

      <nav className="sidebar-nav">
        <div className="section-label">{isCollapsed ? 'Console' : 'Control Panel'}</div>

        <NavLink
          to="/dashboard"
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
          onClick={handleNavClick}
        >
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </NavLink>

        {hasPermission(PERMISSIONS.SEARCH_USER) && (
          <NavLink
            to="/users"
            className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
            onClick={handleNavClick}
          >
            <Users size={20} />
            <span>Users</span>
          </NavLink>
        )}

        <NavLink
          to="/groups"
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
          onClick={handleNavClick}
        >
          <FolderLock size={20} />
          <span>Groups</span>
        </NavLink>

        <NavLink
          to="/roles"
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
          onClick={handleNavClick}
        >
          <UserCheck size={20} />
          <span>Roles</span>
        </NavLink>

        <NavLink
          to="/permissions"
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
          onClick={handleNavClick}
        >
          <ShieldCheck size={20} />
          <span>Permissions</span>
        </NavLink>

        <div className="section-label" style={{ marginTop: '1rem' }}>{isCollapsed ? 'Me' : 'Account'}</div>

        <NavLink
          to="/profile"
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
          onClick={handleNavClick}
        >
          <User size={20} />
          <span>My Profile</span>
        </NavLink>
      </nav>
    </aside>
  );
}
