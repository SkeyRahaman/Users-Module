import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import toast from 'react-hot-toast';
import {
  UserCheck,
  ArrowLeft,
  Users,
  FolderLock,
  ShieldAlert,
  Plus,
  Trash2,
  Lock,
  ShieldCheck
} from 'lucide-react';
import { usePermission } from '../hooks/usePermission.js';
import { PERMISSIONS } from '../utils/constants.js';
import { rolesApi } from '../api/roles.js';
import { usersApi } from '../api/users.js';
import { groupsApi } from '../api/groups.js';
import { permissionsApi } from '../api/permissions.js';
import { Skeleton, SkeletonCard } from '../components/ui/Skeleton.jsx';
import Button from '../components/ui/Button.jsx';
import Tabs from '../components/ui/Tabs.jsx';
import Modal from '../components/ui/Modal.jsx';
import Input from '../components/ui/Input.jsx';
import Can from '../components/ui/Can.jsx';
import EmptyState from '../components/ui/EmptyState.jsx';

export default function RoleDetailPage() {
  const { id } = useParams();
  const roleId = Number(id);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { hasPermission } = usePermission();

  // Modals state
  const [isUserModalOpen, setIsUserModalOpen] = useState(false);
  const [isGroupModalOpen, setIsGroupModalOpen] = useState(false);
  const [isPermModalOpen, setIsPermModalOpen] = useState(false);

  // Form states
  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedGroupId, setSelectedGroupId] = useState('');
  const [selectedPermId, setSelectedPermId] = useState('');
  const [validFrom, setValidFrom] = useState('');
  const [validUntil, setValidUntil] = useState('');

  // Fetch Role details
  const { data: role, isLoading: roleLoading, isError: roleError } = useQuery({
    queryKey: ['roles', roleId],
    queryFn: () => rolesApi.getRoleById(roleId),
    enabled: !isNaN(roleId),
  });

  // Fetch Role sub-resources (Gated by view_roles)
  const canViewRoleDetails = hasPermission(PERMISSIONS.VIEW_ROLES);
  
  const { data: usersWithRole, isLoading: usersLoading } = useQuery({
    queryKey: ['roles', roleId, 'users'],
    queryFn: () => rolesApi.getUsers(roleId),
    enabled: !isNaN(roleId) && canViewRoleDetails,
  });

  const { data: groupsWithRole, isLoading: groupsLoading } = useQuery({
    queryKey: ['roles', roleId, 'groups'],
    queryFn: () => rolesApi.getGroups(roleId),
    enabled: !isNaN(roleId) && canViewRoleDetails,
  });

  const { data: rolePerms, isLoading: permsLoading } = useQuery({
    queryKey: ['roles', roleId, 'permissions'],
    queryFn: () => rolesApi.getPermissions(roleId),
    enabled: !isNaN(roleId) && canViewRoleDetails,
  });

  // Fetch assignable selection options
  const { data: allUsers } = useQuery({
    queryKey: ['users', 'role-assign-selection'],
    queryFn: () => usersApi.getAllUsers({ limit: 100 }),
    enabled: isUserModalOpen,
  });

  const { data: allGroups } = useQuery({
    queryKey: ['groups', 'role-assign-selection'],
    queryFn: groupsApi.getAllGroups,
    enabled: isGroupModalOpen,
  });

  const { data: allPerms } = useQuery({
    queryKey: ['permissions', 'role-assign-selection'],
    queryFn: permissionsApi.getAllPermissions,
    enabled: isPermModalOpen,
  });

  // Mutations
  const assignUserMutation = useMutation({
    mutationFn: (data) => rolesApi.assignUser(roleId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['roles', roleId, 'users'] });
      toast.success('User assigned to role.');
      setIsUserModalOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Assignment failed.');
    }
  });

  const removeUserMutation = useMutation({
    mutationFn: (userId) => rolesApi.removeUser(roleId, userId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['roles', roleId, 'users'] });
      toast.success('User unassigned from role.');
    },
  });

  const assignGroupMutation = useMutation({
    mutationFn: (data) => rolesApi.assignGroup(roleId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['roles', roleId, 'groups'] });
      toast.success('Group assigned to role.');
      setIsGroupModalOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Assignment failed.');
    }
  });

  const removeGroupMutation = useMutation({
    mutationFn: (groupId) => rolesApi.removeGroup(roleId, groupId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['roles', roleId, 'groups'] });
      toast.success('Group unassigned from role.');
    },
  });

  const assignPermMutation = useMutation({
    mutationFn: (data) => rolesApi.assignPermission(roleId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['roles', roleId, 'permissions'] });
      toast.success('Permission granted to role.');
      setIsPermModalOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Permission assignment failed.');
    }
  });

  const removePermMutation = useMutation({
    mutationFn: (permId) => rolesApi.removePermission(roleId, permId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['roles', roleId, 'permissions'] });
      toast.success('Permission removed from role.');
    },
  });

  const handleUserAssign = (e) => {
    e.preventDefault();
    if (!selectedUserId) return;
    assignUserMutation.mutate({
      user_id: Number(selectedUserId),
      valid_from: validFrom || undefined,
      valid_until: validUntil || undefined,
    });
  };

  const handleGroupAssign = (e) => {
    e.preventDefault();
    if (!selectedGroupId) return;
    assignGroupMutation.mutate({
      group_id: Number(selectedGroupId),
      valid_from: validFrom || undefined,
      valid_until: validUntil || undefined,
    });
  };

  const handlePermAssign = (e) => {
    e.preventDefault();
    if (!selectedPermId) return;
    assignPermMutation.mutate({
      permission_id: Number(selectedPermId),
      valid_from: validFrom || undefined,
      valid_until: validUntil || undefined,
    });
  };

  if (roleLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <Skeleton height={100} />
        <SkeletonCard />
      </div>
    );
  }

  if (roleError || !role) {
    return (
      <div className="empty-state">
        <UserCheck size={48} />
        <h2 className="empty-state-title">Role Not Found</h2>
        <p className="empty-state-subtitle">This security role configuration does not exist.</p>
        <Button onClick={() => navigate('/roles')}><ArrowLeft size={16} /> Back to Roles</Button>
      </div>
    );
  }

  const overviewTab = (
    <div className="detail-tab-body info-grid">
      <div className="info-field">
        <span className="info-field-label">Role Name</span>
        <span className="info-field-value">{role.name}</span>
      </div>
      <div className="info-field">
        <span className="info-field-label">Role ID</span>
        <span className="info-field-value">#{role.id}</span>
      </div>
      <div className="info-field">
        <span className="info-field-label">Created At</span>
        <span className="info-field-value">{role.created ? new Date(role.created).toLocaleString() : '—'}</span>
      </div>
      <div className="info-field" style={{ gridColumn: 'span 2' }}>
        <span className="info-field-label">Description</span>
        <span className="info-field-value">{role.description || 'No description provided.'}</span>
      </div>
    </div>
  );

  const usersTab = (
    <div className="detail-tab-body">
      <div className="assignment-panel-header">
        <span className="assignment-panel-title">Users with this Role</span>
        <Can permission={PERMISSIONS.ASSIGN_ROLE_TO_USER}>
          <Button size="sm" onClick={() => { setSelectedUserId(''); setValidFrom(''); setValidUntil(''); setIsUserModalOpen(true); }} style={{ gap: '0.3rem' }}>
            <Plus size={14} /> Assign User
          </Button>
        </Can>
      </div>
      {usersLoading ? (
        <Skeleton height={60} />
      ) : !usersWithRole || usersWithRole.length === 0 ? (
        <EmptyState title="No users assigned" subtitle="No users are directly inheriting this role." />
      ) : (
        <div className="assignment-list">
          {usersWithRole.map((u) => (
            <div className="assignment-item" key={u.id}>
              <div className="assignment-item-info">
                <span className="assignment-item-name">{u.firstname} {u.lastname}</span>
                <span className="assignment-item-meta">@{u.username} • {u.email}</span>
              </div>
              <Can permission={PERMISSIONS.ASSIGN_ROLE_TO_USER}>
                <Button size="sm" variant="ghost" onClick={() => removeUserMutation.mutate(u.id)} icon>
                  <Trash2 size={16} style={{ color: 'var(--danger)' }} />
                </Button>
              </Can>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const groupsTab = (
    <div className="detail-tab-body">
      <div className="assignment-panel-header">
        <span className="assignment-panel-title">Groups with this Role</span>
        <Can permission={PERMISSIONS.ASSIGN_ROLE_TO_USER}>
          <Button size="sm" onClick={() => { setSelectedGroupId(''); setValidFrom(''); setValidUntil(''); setIsGroupModalOpen(true); }} style={{ gap: '0.3rem' }}>
            <Plus size={14} /> Assign Group
          </Button>
        </Can>
      </div>
      {groupsLoading ? (
        <Skeleton height={60} />
      ) : !groupsWithRole || groupsWithRole.length === 0 ? (
        <EmptyState title="No groups assigned" subtitle="No groups are assigned to inherit this role." />
      ) : (
        <div className="assignment-list">
          {groupsWithRole.map((g) => (
            <div className="assignment-item" key={g.id}>
              <div className="assignment-item-info">
                <span className="assignment-item-name">{g.name}</span>
                <span className="assignment-item-meta">{g.description}</span>
              </div>
              <Can permission={PERMISSIONS.ASSIGN_ROLE_TO_USER}>
                <Button size="sm" variant="ghost" onClick={() => removeGroupMutation.mutate(g.id)} icon>
                  <Trash2 size={16} style={{ color: 'var(--danger)' }} />
                </Button>
              </Can>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const permsTab = (
    <div className="detail-tab-body">
      <div className="assignment-panel-header">
        <span className="assignment-panel-title">Role Permissions Configuration</span>
        <Can permission={PERMISSIONS.ASSIGN_ROLE_TO_USER}>
          <Button size="sm" onClick={() => { setSelectedPermId(''); setValidFrom(''); setValidUntil(''); setIsPermModalOpen(true); }} style={{ gap: '0.3rem' }}>
            <Plus size={14} /> Grant Permission
          </Button>
        </Can>
      </div>
      {permsLoading ? (
        <Skeleton height={60} />
      ) : !rolePerms || rolePerms.length === 0 ? (
        <EmptyState title="No permissions granted" subtitle="Grant permission scopes to build this role's capability set." />
      ) : (
        <div className="assignment-list">
          {rolePerms.map((p) => (
            <div className="assignment-item" key={p.id}>
              <div className="assignment-item-info">
                <span className="assignment-item-name">{p.name}</span>
                <span className="assignment-item-meta">{p.description}</span>
              </div>
              <Can permission={PERMISSIONS.ASSIGN_ROLE_TO_USER}>
                <Button size="sm" variant="ghost" onClick={() => removePermMutation.mutate(p.id)} icon>
                  <Trash2 size={16} style={{ color: 'var(--danger)' }} />
                </Button>
              </Can>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <UserCheck size={16} />, content: overviewTab },
    {
      id: 'users',
      label: 'Inherited Users',
      icon: <Users size={16} />,
      content: canViewRoleDetails ? usersTab : <div className="detail-tab-body"><Lock size={32} /><p>Requires role view permissions.</p></div>
    },
    {
      id: 'groups',
      label: 'Inherited Groups',
      icon: <FolderLock size={16} />,
      content: canViewRoleDetails ? groupsTab : <div className="detail-tab-body"><Lock size={32} /><p>Requires role view permissions.</p></div>
    },
    {
      id: 'permissions',
      label: 'Granted Scopes',
      icon: <ShieldCheck size={16} />,
      content: canViewRoleDetails ? permsTab : <div className="detail-tab-body"><Lock size={32} /><p>Requires role view permissions.</p></div>
    }
  ];

  return (
    <div className="animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <Button variant="ghost" onClick={() => navigate('/roles')} style={{ gap: '0.4rem', paddingLeft: 0 }}>
          <ArrowLeft size={16} /> Back to Roles Directory
        </Button>
      </div>

      <div className="profile-header" style={{ flexWrap: 'nowrap' }}>
        <div className="auth-logo-mark" style={{ width: 56, height: 56, borderRadius: 'var(--radius-md)', flexShrink: 0 }}>
          <UserCheck size={28} />
        </div>
        <div className="profile-info" style={{ flex: 1 }}>
          <h2 className="profile-name">{role.name}</h2>
          <p className="profile-username" style={{ margin: 0 }}>{role.description || 'No description configured'}</p>
        </div>
      </div>

      <div className="detail-content">
        <Tabs tabs={tabs} defaultTab="overview" />
      </div>

      {/* Assign User Modal */}
      <Modal isOpen={isUserModalOpen} onClose={() => setIsUserModalOpen(false)} title="Assign User to Role">
        <form onSubmit={handleUserAssign} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Select User Account</label>
            <select
              className="form-input"
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              required
            >
              <option value="">-- Choose User --</option>
              {allUsers?.users?.map((u) => (
                <option key={u.id} value={u.id}>{u.firstname} {u.lastname} (@{u.username})</option>
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
            <Button type="button" variant="secondary" onClick={() => setIsUserModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={assignUserMutation.isPending}>
              Assign User
            </Button>
          </div>
        </form>
      </Modal>

      {/* Assign Group Modal */}
      <Modal isOpen={isGroupModalOpen} onClose={() => setIsGroupModalOpen(false)} title="Assign Group to Role">
        <form onSubmit={handleGroupAssign} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Select User Group</label>
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
            <Button type="submit" loading={assignGroupMutation.isPending}>
              Assign Group
            </Button>
          </div>
        </form>
      </Modal>

      {/* Assign Permission Modal */}
      <Modal isOpen={isPermModalOpen} onClose={() => setIsPermModalOpen(false)} title="Grant Permission Scope to Role">
        <form onSubmit={handlePermAssign} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Select Permission Scope</label>
            <select
              className="form-input"
              value={selectedPermId}
              onChange={(e) => setSelectedPermId(e.target.value)}
              required
            >
              <option value="">-- Choose Permission --</option>
              {allPerms?.map((p) => (
                <option key={p.id} value={p.id}>{p.name} ({p.description})</option>
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
            <Button type="button" variant="secondary" onClick={() => setIsPermModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={assignPermMutation.isPending}>
              Grant Permission
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
