import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import toast from 'react-hot-toast';
import {
  ShieldCheck,
  ArrowLeft,
  UserCheck,
  Plus,
  Trash2,
  Lock
} from 'lucide-react';
import { usePermission } from '../hooks/usePermission.js';
import { PERMISSIONS } from '../utils/constants.js';
import { permissionsApi } from '../api/permissions.js';
import { rolesApi } from '../api/roles.js';
import { Skeleton, SkeletonCard } from '../components/ui/Skeleton.jsx';
import Button from '../components/ui/Button.jsx';
import Tabs from '../components/ui/Tabs.jsx';
import Modal from '../components/ui/Modal.jsx';
import Input from '../components/ui/Input.jsx';
import Can from '../components/ui/Can.jsx';
import EmptyState from '../components/ui/EmptyState.jsx';

export default function PermissionDetailPage() {
  const { id } = useParams();
  const permId = Number(id);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { hasPermission } = usePermission();

  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);

  const [selectedRoleId, setSelectedRoleId] = useState('');
  const [validFrom, setValidFrom] = useState('');
  const [validUntil, setValidUntil] = useState('');

  // Fetch Permission Details
  const { data: perm, isLoading: permLoading, isError: permError } = useQuery({
    queryKey: ['permissions', permId],
    queryFn: () => permissionsApi.getPermissionById(permId),
    enabled: !isNaN(permId),
  });

  // Fetch Roles with this Permission
  const { data: rolesWithPerm, isLoading: rolesLoading } = useQuery({
    queryKey: ['permissions', permId, 'roles'],
    queryFn: () => permissionsApi.getRoles(permId),
    enabled: !isNaN(permId),
  });

  // Fetch all roles for the assign modal dropdown select list
  const { data: allRoles } = useQuery({
    queryKey: ['roles', 'perm-assign-selection'],
    queryFn: rolesApi.getAllRoles,
    enabled: isRoleModalOpen,
  });

  // Mutations
  const assignToRoleMutation = useMutation({
    mutationFn: (data) => permissionsApi.assignToRole(permId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['permissions', permId, 'roles'] });
      toast.success('Permission added to role successfully.');
      setIsRoleModalOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Assignment failed.');
    }
  });

  const removeFromRoleMutation = useMutation({
    mutationFn: (roleId) => permissionsApi.removeFromRole(permId, roleId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['permissions', permId, 'roles'] });
      toast.success('Permission removed from role.');
    },
  });

  const handleRoleAssignSubmit = (e) => {
    e.preventDefault();
    if (!selectedRoleId) return;
    assignToRoleMutation.mutate({
      role_id: Number(selectedRoleId),
      valid_from: validFrom || undefined,
      valid_until: validUntil || undefined,
    });
  };

  if (permLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <Skeleton height={100} />
        <SkeletonCard />
      </div>
    );
  }

  if (permError || !perm) {
    return (
      <div className="empty-state">
        <ShieldCheck size={48} />
        <h2 className="empty-state-title">Scope Not Found</h2>
        <p className="empty-state-subtitle">This permission scope does not exist or has been deleted.</p>
        <Button onClick={() => navigate('/permissions')}><ArrowLeft size={16} /> Back to Scopes</Button>
      </div>
    );
  }

  const overviewTab = (
    <div className="detail-tab-body info-grid">
      <div className="info-field">
        <span className="info-field-label">Scope Name</span>
        <span className="info-field-value">{perm.name}</span>
      </div>
      <div className="info-field">
        <span className="info-field-label">Scope ID</span>
        <span className="info-field-value">#{perm.id}</span>
      </div>
      <div className="info-field">
        <span className="info-field-label">Created At</span>
        <span className="info-field-value">{perm.created ? new Date(perm.created).toLocaleString() : '—'}</span>
      </div>
      <div className="info-field" style={{ gridColumn: 'span 2' }}>
        <span className="info-field-label">Description</span>
        <span className="info-field-value">{perm.description || 'No description configured.'}</span>
      </div>
    </div>
  );

  const rolesTab = (
    <div className="detail-tab-body">
      <div className="assignment-panel-header">
        <span className="assignment-panel-title">Roles inheriting this Scope</span>
        <Can permission={PERMISSIONS.ASSIGN_ROLE_TO_USER}>
          <Button size="sm" onClick={() => { setSelectedRoleId(''); setValidFrom(''); setValidUntil(''); setIsRoleModalOpen(true); }} style={{ gap: '0.3rem' }}>
            <Plus size={14} /> Add to Role
          </Button>
        </Can>
      </div>
      {rolesLoading ? (
        <Skeleton height={60} />
      ) : !rolesWithPerm || rolesWithPerm.length === 0 ? (
        <EmptyState title="Not inherited by any roles" subtitle="Inherit this permission scope inside roles to apply access levels." />
      ) : (
        <div className="assignment-list">
          {rolesWithPerm.map((r) => (
            <div className="assignment-item" key={r.id}>
              <div className="assignment-item-info">
                <span className="assignment-item-name">{r.name}</span>
                <span className="assignment-item-meta">{r.description}</span>
              </div>
              <Can permission={PERMISSIONS.ASSIGN_ROLE_TO_USER}>
                <Button size="sm" variant="ghost" onClick={() => removeFromRoleMutation.mutate(r.id)} icon>
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
    { id: 'overview', label: 'Overview', icon: <ShieldCheck size={16} />, content: overviewTab },
    { id: 'roles', label: 'Associated Roles', icon: <UserCheck size={16} />, content: rolesTab }
  ];

  return (
    <div className="animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <Button variant="ghost" onClick={() => navigate('/permissions')} style={{ gap: '0.4rem', paddingLeft: 0 }}>
          <ArrowLeft size={16} /> Back to Permissions Directory
        </Button>
      </div>

      <div className="profile-header" style={{ flexWrap: 'nowrap' }}>
        <div className="auth-logo-mark" style={{ width: 56, height: 56, borderRadius: 'var(--radius-md)', flexShrink: 0 }}>
          <ShieldCheck size={28} />
        </div>
        <div className="profile-info" style={{ flex: 1 }}>
          <h2 className="profile-name">{perm.name}</h2>
          <p className="profile-username" style={{ margin: 0 }}>{perm.description || 'No description configured'}</p>
        </div>
      </div>

      <div className="detail-content">
        <Tabs tabs={tabs} defaultTab="overview" />
      </div>

      {/* Add to Role Modal */}
      <Modal isOpen={isRoleModalOpen} onClose={() => setIsRoleModalOpen(false)} title="Add Permission Scope to Role">
        <form onSubmit={handleRoleAssignSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
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
            <Button type="submit" loading={assignToRoleMutation.isPending}>
              Assign to Role
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
