import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import toast from 'react-hot-toast';
import { Plus, Edit2, Trash2, ChevronRight, UserCheck, Shield } from 'lucide-react';
import { rolesApi } from '../api/roles.js';
import { usersApi } from '../api/users.js';
import { roleSchema } from '../utils/validators.js';
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

export default function RolesPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { user } = useAuth();
  const { hasPermission } = usePermission();

  // Determine if the user is an admin (has permission to manage roles)
  const isAdmin = hasPermission(PERMISSIONS.VIEW_ROLES);

  // Tabs: 'my-roles' or 'all-roles' (all-roles is admin-only)
  const [activeTab, setActiveTab] = useState('my-roles');
  const [search, setSearch] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);

  // 1. Roles assigned to current user
  const { data: myRoles, isLoading: isMyRolesLoading } = useQuery({
    queryKey: ['roles', 'my-roles', user?.id],
    queryFn: () => usersApi.getUserRoles(user?.id),
    enabled: !!user?.id,
  });

  // 2. All roles (visible to admins only)
  const { data: allRoles, isLoading: isAllRolesLoading } = useQuery({
    queryKey: ['roles', 'all-roles'],
    queryFn: () => rolesApi.getAllRoles(),
    enabled: isAdmin && activeTab === 'all-roles',
  });

  const isLoading = activeTab === 'my-roles' ? isMyRolesLoading : isAllRolesLoading;
  const currentRoles = activeTab === 'my-roles' ? myRoles : allRoles;

  const createMutation = useMutation({
    mutationFn: rolesApi.createRole,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['roles'] });
      toast.success('Role created successfully.');
      setIsCreateOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to create role.');
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => rolesApi.updateRole(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['roles'] });
      toast.success('Role details updated.');
      setIsEditOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to update role.');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => rolesApi.deleteRole(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['roles'] });
      toast.success('Role deleted successfully.');
      setIsDeleteOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to delete role.');
    }
  });

  const {
    register: registerCreate,
    handleSubmit: handleSubmitCreate,
    reset: resetCreate,
    formState: { errors: errorsCreate },
  } = useForm({ resolver: zodResolver(roleSchema) });

  const {
    register: registerEdit,
    handleSubmit: handleSubmitEdit,
    reset: resetEdit,
    formState: { errors: errorsEdit },
  } = useForm({ resolver: zodResolver(roleSchema) });

  const handleCreate = (data) => {
    createMutation.mutate(data);
  };

  const handleEdit = (data) => {
    if (!selectedRole) return;
    updateMutation.mutate({ id: selectedRole.id, data });
  };

  const openEditModal = (role) => {
    setSelectedRole(role);
    resetEdit({
      name: role.name,
      description: role.description || '',
    });
    setIsEditOpen(true);
  };

  const openDeleteModal = (role) => {
    setSelectedRole(role);
    setIsDeleteOpen(true);
  };

  const filteredRoles = currentRoles?.filter(
    (r) =>
      r.name.toLowerCase().includes(search.toLowerCase()) ||
      (r.description && r.description.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="page-header">
        <div className="page-header-info">
          <h1 className="page-title">Security Roles</h1>
          <p className="page-subtitle">Group permission sets and associate them with users or groups</p>
        </div>
        {isAdmin && (
          <div className="page-actions">
            <Button onClick={() => { resetCreate(); setIsCreateOpen(true); }} style={{ gap: '0.4rem' }}>
              <Plus size={16} /> Create Role
            </Button>
          </div>
        )}
      </div>

      {/* Tabs Section */}
      {isAdmin && (
        <div className="tabs-container" style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
          <button
            className={`tab-btn ${activeTab === 'my-roles' ? 'active' : ''}`}
            onClick={() => { setActiveTab('my-roles'); setSearch(''); }}
            style={{
              padding: '0.5rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'my-roles' ? '2px solid var(--accent)' : 'none',
              color: activeTab === 'my-roles' ? 'var(--text-primary)' : 'var(--text-secondary)',
              fontWeight: 'var(--font-medium)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <UserCheck size={16} />
            My Roles
          </button>
          <button
            className={`tab-btn ${activeTab === 'all-roles' ? 'active' : ''}`}
            onClick={() => { setActiveTab('all-roles'); setSearch(''); }}
            style={{
              padding: '0.5rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'all-roles' ? '2px solid var(--accent)' : 'none',
              color: activeTab === 'all-roles' ? 'var(--text-primary)' : 'var(--text-secondary)',
              fontWeight: 'var(--font-medium)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <Shield size={16} />
            All Roles
          </button>
        </div>
      )}

      <div className="card" style={{ padding: '1rem' }}>
        <SearchBar value={search} onChange={setSearch} placeholder="Search roles by name or description..." />
      </div>

      <div className="table-container">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 60 }}>ID</th>
                <th>Role Name</th>
                <th>Description</th>
                <th>Created At</th>
                <th style={{ width: 120 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} cols={5} />)
              ) : !filteredRoles || filteredRoles.length === 0 ? (
                <tr>
                  <td colSpan={5}>
                    <EmptyState
                      icon={<UserCheck size={32} />}
                      title={activeTab === 'my-roles' ? 'No roles assigned' : 'No roles configured'}
                      subtitle={activeTab === 'my-roles' ? 'You are not assigned any security roles.' : 'Create security roles to mapping granular permission scopes.'}
                    />
                  </td>
                </tr>
              ) : (
                filteredRoles.map((r) => (
                  <tr key={r.id}>
                    <td>#{r.id}</td>
                    <td style={{ fontWeight: 'var(--font-medium)', color: 'var(--text-primary)' }}>{r.name}</td>
                    <td>{r.description || '—'}</td>
                    <td>{r.created ? new Date(r.created).toLocaleDateString() : '—'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'center' }}>
                        <Button size="sm" variant="ghost" onClick={() => navigate(`/roles/${r.id}`)} icon>
                          <ChevronRight size={16} />
                        </Button>
                        {isAdmin && (
                          <>
                            <Button size="sm" variant="ghost" onClick={() => openEditModal(r)} icon>
                              <Edit2 size={16} />
                            </Button>
                            <Button size="sm" variant="ghost" onClick={() => openDeleteModal(r)} icon>
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
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Security Role">
        <form className="auth-form" onSubmit={handleSubmitCreate(handleCreate)}>
          <Input
            label="Role Name"
            type="text"
            placeholder="e.g. system_admin"
            error={errorsCreate.name?.message}
            {...registerCreate('name')}
          />
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-input"
              rows={4}
              placeholder="Describe the levels of authority this role grants..."
              {...registerCreate('description')}
            />
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <Button type="button" variant="secondary" onClick={() => setIsCreateOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={createMutation.isPending}>
              Create Role
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Modify Security Role">
        <form className="auth-form" onSubmit={handleSubmitEdit(handleEdit)}>
          <Input
            label="Role Name"
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
        onConfirm={() => deleteMutation.mutate(selectedRole?.id)}
        loading={deleteMutation.isPending}
        title="Delete Security Role?"
        message={`Are you sure you want to delete the role "${selectedRole?.name}"? This will drop authorization for users inheriting it.`}
      />
    </div>
  );
}
