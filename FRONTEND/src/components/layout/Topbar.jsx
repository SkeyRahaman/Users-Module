import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Sun, Moon, LogOut, User as UserIcon, Menu } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth.js';
import { useTheme } from '../../context/ThemeContext.jsx';
import { healthApi } from '../../api/permissions.js';
import Avatar from '../ui/Avatar.jsx';
import Dropdown, { DropdownItem } from '../ui/Dropdown.jsx';

export default function Topbar({ onMobileMenuToggle }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  // Fetch API Health status
  const { data: healthData, isError } = useQuery({
    queryKey: ['health'],
    queryFn: healthApi.check,
    refetchInterval: 30000,
    retry: 1,
  });

  const isHealthy = !isError && (healthData?.status === 'ok' || healthData?.status === 'HEALTHY');

  return (
    <header className="topbar">
      <div className="topbar-left">
        {/* Hamburger — only visible on mobile */}
        <button
          className="topbar-hamburger"
          onClick={onMobileMenuToggle}
          aria-label="Open navigation menu"
        >
          <Menu size={22} />
        </button>

        <div className="api-health-badge">
          <span className={`health-dot ${isHealthy ? 'healthy' : 'unhealthy'}`} />
          <span className="health-badge-text">API: {isHealthy ? 'Healthy' : 'Degraded'}</span>
        </div>
      </div>

      <div className="topbar-right">
        {/* Theme Toggle */}
        <button
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* User Dropdown */}
        {user && (
          <Dropdown
            trigger={
              <div className="user-menu-trigger">
                <Avatar user={user} size="sm" />
                <div className="user-menu-info user-menu-info-hidden-mobile">
                  <span className="user-menu-name">{user.firstname} {user.lastname}</span>
                  <span className="user-menu-role">@{user.username}</span>
                </div>
              </div>
            }
          >
            <DropdownItem onClick={() => navigate('/profile')} icon={<UserIcon size={16} />}>
              My Profile
            </DropdownItem>
            <hr style={{ margin: '4px 0' }} />
            <DropdownItem onClick={logout} danger icon={<LogOut size={16} />}>
              Sign Out
            </DropdownItem>
          </Dropdown>
        )}
      </div>
    </header>
  );
}
