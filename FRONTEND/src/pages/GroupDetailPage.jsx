import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import toast from 'react-hot-toast';
import {
  FolderLock,
  ArrowLeft,
  Users,
  ShieldCheck,
  Plus,
  Trash2,
  Lock,
  Compass
} from 'lucide-react';
import { usePermission } from '../hooks/usePermission.js';
import { PERMISSIONS } from '../utils/constants.js';
import { groupsApi } from '../api/groups.js';
import { rolesApi } from '../api/roles.js';
import { usersApi } from '../api/users.js';
import { Skeleton, SkeletonCard } from '../components/ui/Skeleton.jsx';
import Button from '../components/ui/Button.jsx';
import Tabs from '../components/ui/Tabs.jsx';
import Modal from '../components/ui/Modal.jsx';
import Input from '../components/ui/Input.jsx';
import Can from '../components/ui/Can.jsx';
import EmptyState from '../components/ui/EmptyState.jsx';

export default function GroupDetailPage() {
  const { id } = useParams();
  const groupId = Number(id);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { hasPermission } = usePermission();

  // Modal open states
  const [isMemberModalOpen, setIsMemberModalOpen] = useState(false);
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);

  // Selector states
  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedRoleId, setSelectedRoleId] = useState('');
  const [validFrom, setValidFrom] = useState('');
  const [validUntil, setValidUntil] = useState('');

  // Fetch Group Profile Details
  const { data: group, isLoading: groupLoading, isError: groupError } = useQuery({
    queryKey: ['groups', groupId],
    queryFn: () => groupsApi.getGroupById(groupId),
    enabled: !isNaN(groupId),
  });

  // Fetch Group Members (Gated by remove_user_from_group)
  const canViewMembers = hasPermission(PERMISSIONS.REMOVE_USER_FROM_GROUP);
  const { data: members, isLoading: membersLoading } = useQuery({
    queryKey: ['groups', groupId, 'members'],
    queryFn: () => groupsApi.getUsers(groupId),
    enabled: !isNaN(groupId) && canViewMembers,
  });

  // Fetch Group Roles (Gated by remove_user_from_group)
  const { data: groupRoles, isLoading: rolesLoading } = useQuery({
    queryKey: ['groups', groupId, 'roles'],
    queryFn: () => groupsApi.getRoles(groupId),
    enabled: !isNaN(groupId) && canViewMembers,
  });

  // Fetch options lists for modal dropdown selectors
  const { data: allUsers } = useQuery({
    queryKey: ['users', 'assign-selection'],
    queryFn: () => usersApi.getAllUsers({ limit: 100 }),
    enabled: isMemberModalOpen,
  });

  const { data: allRoles } = useQuery({
    queryKey: ['roles', 'assign-selection'],
    queryFn: rolesApi.getAllRoles,
    enabled: isRoleModalOpen,
  });

  // Mutations
  const addMemberMutation = useMutation({
    mutationFn: (data) => groupsApi.addUser(groupId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['groups', groupId, 'members'] });
      toast.success('User added to group.');
      setIsMemberModalOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Assignment failed.');
    }
  });

  const removeMemberMutation = useMutation({
    mutationFn: (userId) => groupsApi.removeUser(groupId, userId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['groups', groupId, 'members'] });
      toast.success('User removed from group.');
    },
  });

  const assignRoleMutation = useMutation({
    mutationFn: (data) => groupsApi.assignRole(groupId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['groups', groupId, 'roles'] });
      toast.success('Role assigned to group.');
      setIsRoleModalOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Role assignment failed.');
    }
  });

  const removeRoleMutation = useMutation({
    mutationFn: (roleId) => groupsApi.removeRole(groupId, roleId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['groups', groupId, 'roles'] });
      toast.success('Role unassigned from group.');
    },
  });

  const handleAddMemberSubmit = (e) => {
    e.preventDefault();
    if (!selectedUserId) return;
    addMemberMutation.mutate({
      user_id: Number(selectedUserId),
      valid_from: validFrom || undefined,
      valid_until: validUntil || undefined,
    });
  };

  const handleAssignRoleSubmit = (e) => {
    e.preventDefault();
    if (!selectedRoleId) return;
    assignRoleMutation.mutate({
      role_id: Number(selectedRoleId),
      valid_from: validFrom || undefined,
      valid_until: validUntil || undefined,
    });
  };

  if (groupLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <Skeleton height={100} />
        <SkeletonCard />
      </div>
    );
  }

  if (groupError || !group) {
    return (
      <div className="empty-state">
        <FolderLock size={48} />
        <h2 className="empty-state-title">Group Not Found</h2>
        <p className="empty-state-subtitle">The group record does not exist or has been deleted.</p>
        <Button onClick={() => navigate('/groups')}><ArrowLeft size={16} /> Back to Groups</Button>
      </div>
    );
  }

  const overviewTab = (
    <div className="detail-tab-body info-grid">
      <div className="info-field">
        <span className="info-field-label">Group Name</span>
        <span className="info-field-value">{group.name}</span>
      </div>
      <div className="info-field">
        <span className="info-field-label">Group ID</span>
        <span className="info-field-value">#{group.id}</span>
      </div>
      <div className="info-field">
        <span className="info-field-label">Created At</span>
        <span className="info-field-value">{group.created ? new Date(group.created).toLocaleString() : '—'}</span>
      </div>
      <div className="info-field" style={{ gridColumn: 'span 2' }}>
        <span className="info-field-label">Description</span>
        <span className="info-field-value">{group.description || 'No description provided.'}</span>
      </div>
    </div>
  );

  const membersTab = (
    <div className="detail-tab-body">
      <div className="assignment-panel-header">
        <span className="assignment-panel-title">Assigned Group Members</span>
        <Can permission={PERMISSIONS.ASSIGN_USER_TO_GROUP}>
          <Button size="sm" onClick={() => { setSelectedUserId(''); setValidFrom(''); setValidUntil(''); setIsMemberModalOpen(true); }} style={{ gap: '0.3rem' }}>
            <Plus size={14} /> Add User
          </Button>
        </Can>
      </div>
      {membersLoading ? (
        <Skeleton height={60} />
      ) : !members || members.length === 0 ? (
        <EmptyState title="No active members" subtitle="Assign users to this group to apply group security roles." />
      ) : (
        <div className="assignment-list">
          {members.map((u) => (
            <div className="assignment-item" key={u.id}>
              <div className="assignment-item-info">
                <span className="assignment-item-name">{u.firstname} {u.lastname}</span>
                <span className="assignment-item-meta">@{u.username} • {u.email}</span>
              </div>
              <Can permission={PERMISSIONS.REMOVE_USER_FROM_GROUP}>
                <Button size="sm" variant="ghost" onClick={() => removeMemberMutation.mutate(u.id)} icon>
                  <Trash2 size={16} style={{ color: 'var(--danger)' }} />
                </Button>
              </Can>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const rolesTab = (
    <div className="detail-tab-body">
      <div className="assignment-panel-header">
        <span className="assignment-panel-title">Assigned Group Roles</span>
        <Can permission={PERMISSIONS.REMOVE_USER_FROM_GROUP}>
          <Button size="sm" onClick={() => { setSelectedRoleId(''); setValidFrom(''); setValidUntil(''); setIsRoleModalOpen(true); }} style={{ gap: '0.3rem' }}>
            <Plus size={14} /> Assign Role
          </Button>
        </Can>
      </div>
      {rolesLoading ? (
        <Skeleton height={60} />
      ) : !groupRoles || groupRoles.length === 0 ? (
        <EmptyState title="No roles assigned" subtitle="Roles assigned to the group will propagate to all group members." />
      ) : (
        <div className="assignment-list">
          {groupRoles.map((r) => (
            <div className="assignment-item" key={r.id}>
              <div className="assignment-item-info">
                <span className="assignment-item-name">{r.name}</span>
                <span className="assignment-item-meta">{r.description}</span>
              </div>
              <Can permission={PERMISSIONS.REMOVE_USER_FROM_GROUP}>
                <Button size="sm" variant="ghost" onClick={() => removeRoleMutation.mutate(r.id)} icon>
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
    { id: 'overview', label: 'Overview', icon: <FolderLock size={16} />, content: overviewTab },
    {
      id: 'members',
      label: 'Members',
      icon: <Users size={16} />,
      content: canViewMembers ? membersTab : <div className="detail-tab-body"><Lock size={32} /><p>Requires group view permissions.</p></div>
    },
    {
      id: 'roles',
      label: 'Roles Assigned',
      icon: <ShieldCheck size={16} />,
      content: canViewMembers ? rolesTab : <div className="detail-tab-body"><Lock size={32} /><p>Requires group view permissions.</p></div>
    }
  ];

  return (
    <div className="animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <Button variant="ghost" onClick={() => navigate('/groups')} style={{ gap: '0.4rem', paddingLeft: 0 }}>
          <ArrowLeft size={16} /> Back to Groups Directory
        </Button>
      </div>

      <div className="profile-header" style={{ flexWrap: 'nowrap' }}>
        <div className="auth-logo-mark" style={{ width: 56, height: 56, borderRadius: 'var(--radius-md)', flexShrink: 0 }}>
          <FolderLock size={28} />
        </div>
        <div className="profile-info" style={{ flex: 1 }}>
          <h2 className="profile-name">{group.name}</h2>
          <p className="profile-username" style={{ margin: 0 }}>{group.description || 'No description configured'}</p>
        </div>
      </div>

      <div className="detail-content">
        <Tabs tabs={tabs} defaultTab="overview" />
      </div>

      {/* Add User Modal */}
      <Modal isOpen={isMemberModalOpen} onClose={() => setIsMemberModalOpen(false)} title="Add User to Group">
        <form onSubmit={handleAddMemberSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
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
            <Button type="button" variant="secondary" onClick={() => setIsMemberModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={addMemberMutation.isPending}>
              Add User
            </Button>
          </div>
        </form>
      </Modal>

      {/* Assign Role Modal */}
      <Modal isOpen={isRoleModalOpen} onClose={() => setIsRoleModalOpen(false)} title="Assign Role to Group">
        <form onSubmit={handleAssignRoleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Select Security Role</label>
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
              Assign Role
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
