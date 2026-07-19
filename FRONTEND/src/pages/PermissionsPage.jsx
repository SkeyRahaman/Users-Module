import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import toast from 'react-hot-toast';
import { Plus, Edit2, Trash2, ChevronRight, ShieldCheck, Shield, Lock } from 'lucide-react';
import { permissionsApi } from '../api/permissions.js';
import { rolesApi } from '../api/roles.js';
import { usersApi } from '../api/users.js';
import { permissionSchema } from '../utils/validators.js';
import { SkeletonRow } from '../components/ui/Skeleton.jsx';
import { useAuth } from '../hooks/useAuth.js';
import { usePermission } from '../hooks/usePermission.js';
import { PERMISSIONS } from '../utils/constants.js';
import Modal from '../components/ui/Modal.jsx';
import Input from '../components/ui/Input.jsx';
import Button from '../components/ui/Button.jsx';
import SearchBar from '../components/ui/SearchBar.jsx';
import EmptyState from '../components/ui/EmptyState.jsx';
import ConfirmDialog from '../components/ui/ConfirmDialog.jsx';

export default function PermissionsPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { user } = useAuth();
  const { permissions: myPermsSet, hasPermission } = usePermission();

  // Determine if the user is an admin (has permission to view all permission scopes)
  const isAdmin = hasPermission(PERMISSIONS.VIEW_ROLES);

  // Tabs: 'my-permissions' or 'all-permissions' (all-permissions is admin-only)
  const [activeTab, setActiveTab] = useState('my-permissions');
  const [search, setSearch] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [selectedPerm, setSelectedPerm] = useState(null);

  // 1. Permissions assigned to current user (resolved from local set to show detail attributes if available)
  const { data: myRoles } = useQuery({
    queryKey: ['roles', 'my-roles-perms', user?.id],
    queryFn: () => usersApi.getUserRoles(user?.id),
    enabled: !!user?.id,
  });

  const { data: resolvedMyPermissions, isLoading: isMyPermissionsLoading } = useQuery({
    queryKey: ['permissions', 'my-resolved', user?.id],
    queryFn: async () => {
      if (!myRoles || myRoles.length === 0) return [];
      const sets = await Promise.allSettled(
        myRoles.map((r) => rolesApi.getPermissions(r.id))
      );
      const uniquePerms = [];
      const seen = new Set();
      sets.forEach((res) => {
        if (res.status === 'fulfilled' && Array.isArray(res.value)) {
          res.value.forEach((p) => {
            if (!seen.has(p.id)) {
              seen.add(p.id);
              uniquePerms.push(p);
            }
          });
        }
      });
      return uniquePerms;
    },
    enabled: !!myRoles && myRoles.length > 0,
  });

  // 2. All permissions (visible to admins only)
  const { data: allPermissions, isLoading: isAllPermissionsLoading } = useQuery({
    queryKey: ['permissions', 'all-list'],
    queryFn: () => permissionsApi.getAllPermissions(),
    enabled: isAdmin && activeTab === 'all-permissions',
  });

  const isLoading = activeTab === 'my-permissions' ? (myRoles && myRoles.length > 0 ? isMyPermissionsLoading : false) : isAllPermissionsLoading;
  const currentPermissions = activeTab === 'my-permissions' ? (resolvedMyPermissions || []) : allPermissions;

  const createMutation = useMutation({
    mutationFn: permissionsApi.createPermission,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['permissions'] });
      toast.success('Permission scope created.');
      setIsCreateOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to create permission.');
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => permissionsApi.updatePermission(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['permissions'] });
      toast.success('Permission scope updated.');
      setIsEditOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to update permission.');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => permissionsApi.deletePermission(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['permissions'] });
      toast.success('Permission scope deleted successfully.');
      setIsDeleteOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to delete permission.');
    }
  });

  const {
    register: registerCreate,
    handleSubmit: handleSubmitCreate,
    reset: resetCreate,
    formState: { errors: errorsCreate },
  } = useForm({ resolver: zodResolver(permissionSchema) });

  const {
    register: registerEdit,
    handleSubmit: handleSubmitEdit,
    reset: resetEdit,
    formState: { errors: errorsEdit },
  } = useForm({ resolver: zodResolver(permissionSchema) });

  const handleCreate = (data) => {
    createMutation.mutate(data);
  };

  const handleEdit = (data) => {
    if (!selectedPerm) return;
    updateMutation.mutate({ id: selectedPerm.id, data });
  };

  const openEditModal = (perm) => {
    setSelectedPerm(perm);
    resetEdit({
      name: perm.name,
      description: perm.description || '',
    });
    setIsEditOpen(true);
  };

  const openDeleteModal = (perm) => {
    setSelectedPerm(perm);
    setIsDeleteOpen(true);
  };

  const filteredPerms = currentPermissions?.filter(
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      (p.description && p.description.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="page-header">
        <div className="page-header-info">
          <h1 className="page-title">RBAC Permissions</h1>
          <p className="page-subtitle">Configure granular API scopes and permission parameters</p>
        </div>
        {isAdmin && (
          <div className="page-actions">
            <Button onClick={() => { resetCreate(); setIsCreateOpen(true); }} style={{ gap: '0.4rem' }}>
              <Plus size={16} /> Create Scope
            </Button>
          </div>
        )}
      </div>

      {/* Tabs Section */}
      {isAdmin && (
        <div className="tabs-container" style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
          <button
            className={`tab-btn ${activeTab === 'my-permissions' ? 'active' : ''}`}
            onClick={() => { setActiveTab('my-permissions'); setSearch(''); }}
            style={{
              padding: '0.5rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'my-permissions' ? '2px solid var(--accent)' : 'none',
              color: activeTab === 'my-permissions' ? 'var(--text-primary)' : 'var(--text-secondary)',
              fontWeight: 'var(--font-medium)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <Lock size={16} />
            My Permissions
          </button>
          <button
            className={`tab-btn ${activeTab === 'all-permissions' ? 'active' : ''}`}
            onClick={() => { setActiveTab('all-permissions'); setSearch(''); }}
            style={{
              padding: '0.5rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'all-permissions' ? '2px solid var(--accent)' : 'none',
              color: activeTab === 'all-permissions' ? 'var(--text-primary)' : 'var(--text-secondary)',
              fontWeight: 'var(--font-medium)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <Shield size={16} />
            All Permissions
          </button>
        </div>
      )}

      <div className="card" style={{ padding: '1rem' }}>
        <SearchBar value={search} onChange={setSearch} placeholder="Search permission scopes by name..." />
      </div>

      <div className="table-container">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 60 }}>ID</th>
                <th>Scope Name</th>
                <th>Description</th>
                <th>Created At</th>
                <th style={{ width: 120 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} cols={5} />)
              ) : !filteredPerms || filteredPerms.length === 0 ? (
                <tr>
                  <td colSpan={5}>
                    <EmptyState
                      icon={<ShieldCheck size={32} />}
                      title={activeTab === 'my-permissions' ? 'No permissions assigned' : 'No permissions configured'}
                      subtitle={activeTab === 'my-permissions' ? 'You do not hold any permissions.' : 'Create scopes to represent granular backend operations.'}
                    />
                  </td>
                </tr>
              ) : (
                filteredPerms.map((p) => (
                  <tr key={p.id}>
                    <td>#{p.id}</td>
                    <td style={{ fontWeight: 'var(--font-medium)', color: 'var(--text-primary)' }}>{p.name}</td>
                    <td>{p.description || '—'}</td>
                    <td>{p.created ? new Date(p.created).toLocaleDateString() : '—'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'center' }}>
                        <Button size="sm" variant="ghost" onClick={() => navigate(`/permissions/${p.id}`)} icon>
                          <ChevronRight size={16} />
                        </Button>
                        {isAdmin && (
                          <>
                            <Button size="sm" variant="ghost" onClick={() => openEditModal(p)} icon>
                              <Edit2 size={16} />
                            </Button>
                            <Button size="sm" variant="ghost" onClick={() => openDeleteModal(p)} icon>
                              <Trash2 size={16} style={{ color: 'var(--danger)' }} />
                            </Button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Permission Scope">
        <form className="auth-form" onSubmit={handleSubmitCreate(handleCreate)}>
          <Input
            label="Scope Name"
            type="text"
            placeholder="e.g. view_reports"
            error={errorsCreate.name?.message}
            {...registerCreate('name')}
          />
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-input"
              rows={4}
              placeholder="Describe the backend resources and actions this scope gates..."
              {...registerCreate('description')}
            />
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <Button type="button" variant="secondary" onClick={() => setIsCreateOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={createMutation.isPending}>
              Create Scope
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Modify Permission Scope">
        <form className="auth-form" onSubmit={handleSubmitEdit(handleEdit)}>
          <Input
            label="Scope Name"
            type="text"
            error={errorsEdit.name?.message}
            {...registerEdit('name')}
          />
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-input"
              rows={4}
              {...registerEdit('description')}
            />
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <Button type="button" variant="secondary" onClick={() => setIsEditOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={updateMutation.isPending}>
              Save Changes
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Dialog */}
      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate(selectedPerm?.id)}
        loading={deleteMutation.isPending}
        title="Delete Permission Scope?"
        message={`Are you sure you want to delete the permission "${selectedPerm?.name}"?`}
      />
    </div>
  );
}
