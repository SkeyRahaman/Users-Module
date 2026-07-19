import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import toast from 'react-hot-toast';
import {
  User,
  ShieldCheck,
  FolderLock,
  History,
  ArrowLeft,
  Lock,
  Plus,
  Trash2,
  Calendar,
  Settings,
  Mail,
  UserCheck
} from 'lucide-react';
import { usePermission } from '../hooks/usePermission.js';
import { PERMISSIONS } from '../utils/constants.js';
import { usersApi } from '../api/users.js';
import { rolesApi } from '../api/roles.js';
import { groupsApi } from '../api/groups.js';
import { Skeleton, SkeletonCard } from '../components/ui/Skeleton.jsx';
import Button from '../components/ui/Button.jsx';
import Tabs from '../components/ui/Tabs.jsx';
import Avatar from '../components/ui/Avatar.jsx';
import Modal from '../components/ui/Modal.jsx';
import Input from '../components/ui/Input.jsx';
import Can from '../components/ui/Can.jsx';
import EmptyState from '../components/ui/EmptyState.jsx';

export default function UserDetailPage() {
  const { id } = useParams();
  const userId = Number(id);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { hasPermission } = usePermission();

  // Assignment Modal states
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [isGroupModalOpen, setIsGroupModalOpen] = useState(false);

  // Form states
  const [selectedRoleId, setSelectedRoleId] = useState('');
  const [selectedGroupId, setSelectedGroupId] = useState('');
  const [validFrom, setValidFrom] = useState('');
  const [validUntil, setValidUntil] = useState('');

  // 1. Fetch User Main profile details
  const { data: user, isLoading: userLoading, isError: userError } = useQuery({
    queryKey: ['users', userId],
    queryFn: () => usersApi.getUserById(userId),
    enabled: !isNaN(userId),
  });

  // 2. Fetch User Relations (Only if user is loaded and permission matches)
  const canAssignRoles = hasPermission(PERMISSIONS.ASSIGN_ROLE_TO_USER);
  const { data: userRoles, isLoading: rolesLoading } = useQuery({
    queryKey: ['users', userId, 'roles'],
    queryFn: () => usersApi.getUserRoles(userId),
    enabled: !isNaN(userId) && canAssignRoles,
  });

  const canRemoveFromGroup = hasPermission(PERMISSIONS.REMOVE_USER_FROM_GROUP);
  const { data: userGroups, isLoading: groupsLoading } = useQuery({
    queryKey: ['users', userId, 'groups'],
    queryFn: () => usersApi.getUserGroups(userId),
    enabled: !isNaN(userId) && canRemoveFromGroup,
  });

  const canViewLogs = hasPermission(PERMISSIONS.VIEW_AUDIT_LOGS);
  const { data: logsData, isLoading: logsLoading } = useQuery({
    queryKey: ['users', userId, 'activity'],
    queryFn: () => usersApi.getActivityLogs(userId),
    enabled: !isNaN(userId) && canViewLogs,
  });

  // Role and Group query lists (for selection drop-downs)
  const { data: allRoles } = useQuery({
    queryKey: ['roles', 'assign-list'],
    queryFn: rolesApi.getAllRoles,
    enabled: isRoleModalOpen,
  });

  const { data: allGroups } = useQuery({
    queryKey: ['groups', 'assign-list'],
    queryFn: groupsApi.getAllGroups,
    enabled: isGroupModalOpen,
  });

  // Mutations
  const activateMutation = useMutation({
    mutationFn: () => usersApi.activateUser(userId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users', userId] });
      toast.success('User profile activated.');
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: () => usersApi.deactivateUser(userId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users', userId] });
      toast.success('User profile deactivated.');
    },
  });

  const assignRoleMutation = useMutation({
    mutationFn: (data) => usersApi.assignRole(userId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users', userId, 'roles'] });
      toast.success('Role assigned to user.');
      setIsRoleModalOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Assignment failed.');
    }
  });

  const removeRoleMutation = useMutation({
    mutationFn: (roleId) => usersApi.removeRole(userId, roleId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users', userId, 'roles'] });
      toast.success('Role unassigned.');
    },
  });

  const addToGroupMutation = useMutation({
    mutationFn: (data) => usersApi.addToGroup(userId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users', userId, 'groups'] });
      toast.success('User added to group.');
      setIsGroupModalOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Group assignment failed.');
    }
  });

  const removeFromGroupMutation = useMutation({
    mutationFn: (groupId) => usersApi.removeFromGroup(userId, groupId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users', userId, 'groups'] });
      toast.success('User removed from group.');
    },
  });

  const handleRoleAssign = (e) => {
    e.preventDefault();
    if (!selectedRoleId) return;
    assignRoleMutation.mutate({
      role_id: Number(selectedRoleId),
      valid_from: validFrom || undefined,
      valid_until: validUntil || undefined,
    });
  };

  const handleGroupAssign = (e) => {
    e.preventDefault();
    if (!selectedGroupId) return;
    addToGroupMutation.mutate({
      group_id: Number(selectedGroupId),
      valid_from: validFrom || undefined,
      valid_until: validUntil || undefined,
    });
  };

  if (userLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <Skeleton height={120} />
        <SkeletonCard />
      </div>
    );
  }

  if (userError || !user) {
    return (
      <div className="empty-state">
        <ShieldCheck size={48} />
        <h2 className="empty-state-title">User Not Found</h2>
        <p className="empty-state-subtitle">The user account may have been permanently deleted or is inaccessible.</p>
        <Button onClick={() => navigate('/users')}><ArrowLeft size={16} /> Back to Directory</Button>
      </div>
    );
  }

  const userDisplayName = `${user.firstname} ${user.lastname}`;

  const overviewTab = (
    <div className="detail-tab-body info-grid">
      <div className="info-field">
        <span className="info-field-label">Username</span>
        <span className="info-field-value">@{user.username}</span>
      </div>
      <div className="info-field">
        <span className="info-field-label">Email Address</span>
        <span className="info-field-value">{user.email}</span>
      </div>
      <div className="info-field">
        <span className="info-field-label">User ID</span>
        <span className="info-field-value">{user.id}</span>
      </div>
      <div className="info-field">
        <span className="info-field-label">Registered At</span>
        <span className="info-field-value">{user.created ? new Date(user.created).toLocaleString() : '—'}</span>
      </div>
    </div>
  );

  const rolesTab = (
    <div className="detail-tab-body">
      <div className="assignment-panel-header">
        <span className="assignment-panel-title">Assigned Roles Mapping</span>
        <Button size="sm" onClick={() => { setSelectedRoleId(''); setValidFrom(''); setValidUntil(''); setIsRoleModalOpen(true); }} style={{ gap: '0.3rem' }}>
          <Plus size={14} /> Assign Role
        </Button>
      </div>
      {rolesLoading ? (
        <Skeleton height={60} />
      ) : !userRoles || userRoles.length === 0 ? (
        <EmptyState title="No assigned roles" subtitle="Assign roles to delegate permissions to this user." />
      ) : (
        <div className="assignment-list">
          {userRoles.map((ur) => (
            <div className="assignment-item" key={ur.id}>
              <div className="assignment-item-info">
                <span className="assignment-item-name">{ur.name}</span>
                <span className="assignment-item-meta">{ur.description}</span>
              </div>
              <Button size="sm" variant="ghost" onClick={() => removeRoleMutation.mutate(ur.id)} icon>
                <Trash2 size={16} style={{ color: 'var(--danger)' }} />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const groupsTab = (
    <div className="detail-tab-body">
      <div className="assignment-panel-header">
        <span className="assignment-panel-title">Direct Group Memberships</span>
        <Can permission={PERMISSIONS.ASSIGN_USER_TO_GROUP}>
          <Button size="sm" onClick={() => { setSelectedGroupId(''); setValidFrom(''); setValidUntil(''); setIsGroupModalOpen(true); }} style={{ gap: '0.3rem' }}>
            <Plus size={14} /> Add to Group
          </Button>
        </Can>
      </div>
      {groupsLoading ? (
        <Skeleton height={60} />
      ) : !userGroups || userGroups.length === 0 ? (
        <EmptyState title="No group memberships" subtitle="Groups bundle common roles for easier batch operations." />
      ) : (
        <div className="assignment-list">
          {userGroups.map((ug) => (
            <div className="assignment-item" key={ug.id}>
              <div className="assignment-item-info">
                <span className="assignment-item-name">{ug.name}</span>
                <span className="assignment-item-meta">{ug.description}</span>
              </div>
              <Button size="sm" variant="ghost" onClick={() => removeFromGroupMutation.mutate(ug.id)} icon>
                <Trash2 size={16} style={{ color: 'var(--danger)' }} />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const logsTab = (
    <div className="detail-tab-body">
      <h3 style={{ fontSize: '1rem', marginBottom: '1.25rem' }}>Audit Event Timeline</h3>
      {logsLoading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Skeleton height={30} />
          <Skeleton height={30} />
        </div>
      ) : !logsData || !logsData.activities || logsData.activities.length === 0 ? (
        <EmptyState title="No logs found" subtitle="No actions have been registered for this account." />
      ) : (
        <div className="timeline-container">
          {logsData.activities.map((log, index) => (
            <div className="timeline-item" key={index}>
              <div className="timeline-icon login">
                <History size={16} />
              </div>
              <div className="timeline-body">
                <p className="timeline-action">{log.event}</p>
                <span className="timeline-time">{log.method} {log.path} • {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'Recent'}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Tab definitions
  const tabs = [
    { id: 'overview', label: 'Overview', icon: <User size={16} />, content: overviewTab },
    {
      id: 'roles',
      label: 'Security Roles',
      icon: <ShieldCheck size={16} />,
      content: canAssignRoles ? rolesTab : <div className="detail-tab-body"><Lock size={32} /><p>Requires role scope permission.</p></div>
    },
    {
      id: 'groups',
      label: 'Memberships',
      icon: <FolderLock size={16} />,
      content: canRemoveFromGroup ? groupsTab : <div className="detail-tab-body"><Lock size={32} /><p>Requires group scope permission.</p></div>
    },
    {
      id: 'logs',
      label: 'Audit Trail',
      icon: <History size={16} />,
      content: canViewLogs ? logsTab : <div className="detail-tab-body"><Lock size={32} /><p>Requires view_audit_logs permission.</p></div>
    }
  ];

  return (
    <div className="animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Return button */}
      <div>
        <Button variant="ghost" onClick={() => navigate('/users')} style={{ gap: '0.4rem', paddingLeft: 0 }}>
          <ArrowLeft size={16} /> Back to Users Directory
        </Button>
      </div>

      {/* Profile Header card */}
      <div className="profile-header">
        <Avatar user={user} size="lg" />
        <div className="profile-info">
          <h2 className="profile-name">{userDisplayName}</h2>
          <p className="profile-username">@{user.username} • {user.email}</p>
          <div className="profile-meta">
            <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`} dot>
              {user.is_active ? 'Active Account' : 'Deactivated'}
            </span>
          </div>
        </div>

        <div className="profile-actions">
          <Can permission={PERMISSIONS.ACTIVATE_USER}>
            {!user.is_active && (
              <Button variant="success" onClick={() => activateMutation.mutate()} loading={activateMutation.isPending}>
                Activate Profile
              </Button>
            )}
          </Can>
          <Can permission={PERMISSIONS.DEACTIVATE_USER}>
            {user.is_active && (
              <Button variant="danger" onClick={() => deactivateMutation.mutate()} loading={deactivateMutation.isPending}>
                Deactivate Profile
              </Button>
            )}
          </Can>
        </div>
      </div>

      {/* Tabs panels */}
      <div className="detail-content">
        <Tabs tabs={tabs} defaultTab="overview" />
      </div>

      {/* Assign Role Modal */}
      <Modal isOpen={isRoleModalOpen} onClose={() => setIsRoleModalOpen(false)} title="Assign Role Assignment">
        <form onSubmit={handleRoleAssign} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Select Role</label>
            <select
              className="form-input"
              value={selectedRoleId}
              onChange={(e) => setSelectedRoleId(e.target.value)}
              required
            >
              <option value="">-- Choose Role --</option>
              {allRoles?.map((r) => (
                <option key={r.id} value={r.id}>{r.name} ({r.description})</option>
              ))}
            </select>
          </div>

          <Input
            label="Valid From"
            type="datetime-local"
            value={validFrom}
            onChange={(e) => setValidFrom(e.target.value)}
          />

          <Input
            label="Valid Until"
            type="datetime-local"
            value={validUntil}
            onChange={(e) => setValidUntil(e.target.value)}
          />

          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <Button type="button" variant="secondary" onClick={() => setIsRoleModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={assignRoleMutation.isPending}>
              Confirm Assignment
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Group Modal */}
      <Modal isOpen={isGroupModalOpen} onClose={() => setIsGroupModalOpen(false)} title="Add Group Membership">
        <form onSubmit={handleGroupAssign} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Select Group</label>
            <select
              className="form-input"
              value={selectedGroupId}
              onChange={(e) => setSelectedGroupId(e.target.value)}
              required
            >
              <option value="">-- Choose Group --</option>
              {allGroups?.map((g) => (
                <option key={g.id} value={g.id}>{g.name} ({g.description})</option>
              ))}
            </select>
          </div>

          <Input
            label="Valid From"
            type="datetime-local"
            value={validFrom}
            onChange={(e) => setValidFrom(e.target.value)}
          />

          <Input
            label="Valid Until"
            type="datetime-local"
            value={validUntil}
            onChange={(e) => setValidUntil(e.target.value)}
          />

          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <Button type="button" variant="secondary" onClick={() => setIsGroupModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={addToGroupMutation.isPending}>
              Confirm Membership
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
