import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  FolderLock,
  UserCheck,
  ShieldCheck,
  TrendingUp,
  UserPlus,
  Compass,
  Lock,
  History
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { usePermission } from '../hooks/usePermission.js';
import { PERMISSIONS } from '../utils/constants.js';
import { usersApi } from '../api/users.js';
import { groupsApi } from '../api/groups.js';
import { rolesApi } from '../api/roles.js';
import { permissionsApi } from '../api/permissions.js';
import { Skeleton } from '../components/ui/Skeleton.jsx';
import Can from '../components/ui/Can.jsx';

// Premium Mock growth details
const chartData = [
  { name: 'Jan', Users: 12 },
  { name: 'Feb', Users: 19 },
  { name: 'Mar', Users: 32 },
  { name: 'Apr', Users: 48 },
  { name: 'May', Users: 64 },
  { name: 'Jun', Users: 89 },
  { name: 'Jul', Users: 120 },
];

export default function DashboardPage() {
  const { hasPermission } = usePermission();
  const navigate = useNavigate();

  // Queries (enabled by permission checking where required)
  const canSearchUsers = hasPermission(PERMISSIONS.SEARCH_USER);

  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ['users', 'dashboard-count'],
    queryFn: () => usersApi.getAllUsers({ limit: 1 }),
    enabled: canSearchUsers,
  });

  const { data: groupsData, isLoading: groupsLoading } = useQuery({
    queryKey: ['groups', 'dashboard-count'],
    queryFn: () => groupsApi.getAllGroups({ limit: 1 }),
  });

  const { data: rolesData, isLoading: rolesLoading } = useQuery({
    queryKey: ['roles', 'dashboard-count'],
    queryFn: () => rolesApi.getAllRoles({ limit: 1 }),
  });

  const { data: permissionsData, isLoading: permissionsLoading } = useQuery({
    queryKey: ['permissions', 'dashboard-count'],
    queryFn: () => permissionsApi.getAllPermissions({ limit: 1 }),
  });

  // Fetch recent activity logs of the current user
  const { data: currentUser } = useQuery({
    queryKey: ['users', 'me'],
    queryFn: usersApi.getMe,
  });

  const { data: activityLogs, isLoading: logsLoading } = useQuery({
    queryKey: ['users', currentUser?.id, 'activity', { limit: 5 }],
    queryFn: () => usersApi.getActivityLogs(currentUser.id, { limit: 5, offset: 0 }),
    enabled: !!currentUser && hasPermission(PERMISSIONS.VIEW_AUDIT_LOGS),
  });

  const stats = [
    {
      id: 'users',
      label: 'Total Users',
      value: usersData?.total ?? 0,
      loading: usersLoading,
      icon: <Users size={22} />,
      color: 'violet',
      permission: PERMISSIONS.SEARCH_USER,
    },
    {
      id: 'groups',
      label: 'User Groups',
      value: groupsData?.length ?? 0,
      loading: groupsLoading,
      icon: <FolderLock size={22} />,
      color: 'info',
    },
    {
      id: 'roles',
      label: 'Security Roles',
      value: rolesData?.length ?? 0,
      loading: rolesLoading,
      icon: <UserCheck size={22} />,
      color: 'success',
    },
    {
      id: 'permissions',
      label: 'RBAC Scopes',
      value: permissionsData?.length ?? 0,
      loading: permissionsLoading,
      icon: <ShieldCheck size={22} />,
      color: 'warning',
    },
  ];

  return (
    <div className="animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div className="page-header">
        <div className="page-header-info">
          <h1 className="page-title">Dashboard Overview</h1>
          <p className="page-subtitle">Security parameters, role scopes, and system operations summary</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="dashboard-stats">
        {stats.map((stat) => {
          const CardContent = (
            <div className="stat-card" key={stat.id}>
              <div className={`stat-card-icon ${stat.color}`}>{stat.icon}</div>
              <div className="stat-card-body">
                {stat.loading ? (
                  <Skeleton width="60%" height={24} />
                ) : (
                  <span className="stat-value">{stat.value}</span>
                )}
                <span className="stat-label">{stat.label}</span>
              </div>
            </div>
          );

          if (stat.permission) {
            return (
              <Can permission={stat.permission} key={stat.id}>
                {CardContent}
              </Can>
            );
          }
          return CardContent;
        })}
      </div>

      {/* Main Grid */}
      <div className="dashboard-grid">
        {/* Left Column: Chart — admin only */}
        <Can permission={PERMISSIONS.SEARCH_USER}>
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <TrendingUp size={18} /> User Growth Trends
              </h2>
            </div>

            <div style={{ width: '100%', height: 300, marginTop: '1rem' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="var(--accent)" stopOpacity={0.01} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      background: 'var(--bg-secondary)',
                      borderColor: 'var(--border)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--text-primary)',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="Users"
                    stroke="var(--accent)"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorUsers)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Can>

        {/* Right Column: Actions / Activity */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Quick Actions — admin only */}
          <Can permission={PERMISSIONS.SEARCH_USER}>
            <div className="card">
              <h2 className="card-title">Console Actions</h2>
              <div className="quick-actions-grid">
                <button className="quick-action-btn" onClick={() => navigate('/users')}>
                  <div className="quick-action-icon"><UserPlus size={16} /></div>
                  <span>Create User</span>
                </button>
                
                <button className="quick-action-btn" onClick={() => navigate('/groups')}>
                  <div className="quick-action-icon"><FolderLock size={16} /></div>
                  <span>New Group</span>
                </button>
                
                <button className="quick-action-btn" onClick={() => navigate('/roles')}>
                  <div className="quick-action-icon"><UserCheck size={16} /></div>
                  <span>New Role</span>
                </button>

                <button className="quick-action-btn" onClick={() => navigate('/permissions')}>
                  <div className="quick-action-icon"><ShieldCheck size={16} /></div>
                  <span>New Permission</span>
                </button>
              </div>
            </div>
          </Can>

          {/* User Activity Timeline */}
          <div className="card">
            <h2 className="card-title" style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <History size={18} /> My Recent Activity
            </h2>

            <Can
              permission={PERMISSIONS.VIEW_AUDIT_LOGS}
              fallback={
                <div className="empty-state" style={{ padding: '2rem 1rem' }}>
                  <Lock size={24} />
                  <p className="empty-state-title">Logs Not Available</p>
                  <p className="empty-state-subtitle">Activity log access requires elevated privileges.</p>
                </div>
              }
            >
              {logsLoading ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem', padding: '1rem 0' }}>
                  <Skeleton height={40} />
                  <Skeleton height={40} />
                  <Skeleton height={40} />
                </div>
              ) : !activityLogs || !activityLogs.activities || activityLogs.activities.length === 0 ? (
                <div className="empty-state" style={{ padding: '2rem 1rem' }}>
                  <History size={24} />
                  <p className="empty-state-subtitle">No logged events found for your session.</p>
                </div>
              ) : (
                <div className="activity-feed">
                  {activityLogs.activities.map((log, idx) => (
                    <div className="activity-item stagger-item" key={idx}>
                      <div className="activity-icon info">
                        <Compass size={14} />
                      </div>
                      <div className="activity-body">
                        <p className="activity-description">{log.event}</p>
                        <div className="activity-meta">
                          <span>{log.method} {log.path}</span>
                          <span>•</span>
                          <span>{log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'Recent'}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Can>
          </div>
        </div>
      </div>
    </div>
  );
}
