import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import toast from 'react-hot-toast';
import { Plus, ArrowUpDown, Trash2, Edit2, ChevronRight, FolderLock, UserCheck, Shield } from 'lucide-react';
import { groupsApi } from '../api/groups.js';
import { usersApi } from '../api/users.js';
import { groupSchema } from '../utils/validators.js';
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

export default function GroupsPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { user } = useAuth();
  const { hasPermission } = usePermission();

  // Determine if the user is an admin (has permission to manage groups)
  const isAdmin = hasPermission(PERMISSIONS.REMOVE_USER_FROM_GROUP);

  // Tabs: 'my-groups' or 'all-groups' (all-groups is admin-only)
  const [activeTab, setActiveTab] = useState('my-groups');
  const [search, setSearch] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);

  // 1. Groups assigned to current user
  const { data: myGroups, isLoading: isMyGroupsLoading } = useQuery({
    queryKey: ['groups', 'my-groups', user?.id],
    queryFn: () => usersApi.getUserGroups(user?.id),
    enabled: !!user?.id,
  });

  // 2. All groups (visible to admins only)
  const { data: allGroups, isLoading: isAllGroupsLoading } = useQuery({
    queryKey: ['groups', 'all-groups'],
    queryFn: () => groupsApi.getAllGroups(),
    enabled: isAdmin && activeTab === 'all-groups',
  });

  const isLoading = activeTab === 'my-groups' ? isMyGroupsLoading : isAllGroupsLoading;
  const currentGroups = activeTab === 'my-groups' ? myGroups : allGroups;

  const createMutation = useMutation({
    mutationFn: groupsApi.createGroup,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['groups'] });
      toast.success('Group created successfully.');
      setIsCreateOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to create group.');
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => groupsApi.updateGroup(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['groups'] });
      toast.success('Group updated successfully.');
      setIsEditOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to update group.');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => groupsApi.deleteGroup(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['groups'] });
      toast.success('Group deleted successfully.');
      setIsDeleteOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to delete group.');
    }
  });

  const {
    register: registerCreate,
    handleSubmit: handleSubmitCreate,
    reset: resetCreate,
    formState: { errors: errorsCreate },
  } = useForm({ resolver: zodResolver(groupSchema) });

  const {
    register: registerEdit,
    handleSubmit: handleSubmitEdit,
    reset: resetEdit,
    formState: { errors: errorsEdit },
  } = useForm({ resolver: zodResolver(groupSchema) });

  const handleCreate = (data) => {
    createMutation.mutate(data);
  };

  const handleEdit = (data) => {
    if (!selectedGroup) return;
    updateMutation.mutate({ id: selectedGroup.id, data });
  };

  const openEditModal = (group) => {
    setSelectedGroup(group);
    resetEdit({
      name: group.name,
      description: group.description || '',
    });
    setIsEditOpen(true);
  };

  const openDeleteModal = (group) => {
    setSelectedGroup(group);
    setIsDeleteOpen(true);
  };

  // Filter groups locally based on search bar
  const filteredGroups = currentGroups?.filter(
    (g) =>
      g.name.toLowerCase().includes(search.toLowerCase()) ||
      (g.description && g.description.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="page-header">
        <div className="page-header-info">
          <h1 className="page-title">User Groups</h1>
          <p className="page-subtitle">Granular access group configurations for team member categorization</p>
        </div>
        {isAdmin && (
          <div className="page-actions">
            <Button onClick={() => { resetCreate(); setIsCreateOpen(true); }} style={{ gap: '0.4rem' }}>
              <Plus size={16} /> Create Group
            </Button>
          </div>
        )}
      </div>

      {/* Tabs Section */}
      {isAdmin && (
        <div className="tabs-container" style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
          <button
            className={`tab-btn ${activeTab === 'my-groups' ? 'active' : ''}`}
            onClick={() => { setActiveTab('my-groups'); setSearch(''); }}
            style={{
              padding: '0.5rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'my-groups' ? '2px solid var(--accent)' : 'none',
              color: activeTab === 'my-groups' ? 'var(--text-primary)' : 'var(--text-secondary)',
              fontWeight: 'var(--font-medium)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <UserCheck size={16} />
            My Groups
          </button>
          <button
            className={`tab-btn ${activeTab === 'all-groups' ? 'active' : ''}`}
            onClick={() => { setActiveTab('all-groups'); setSearch(''); }}
            style={{
              padding: '0.5rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'all-groups' ? '2px solid var(--accent)' : 'none',
              color: activeTab === 'all-groups' ? 'var(--text-primary)' : 'var(--text-secondary)',
              fontWeight: 'var(--font-medium)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <Shield size={16} />
            All Groups
          </button>
        </div>
      )}

      <div className="card" style={{ padding: '1rem' }}>
        <SearchBar value={search} onChange={setSearch} placeholder="Search groups by name or description..." />
      </div>

      <div className="table-container">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 60 }}>ID</th>
                <th>Group Name</th>
                <th>Description</th>
                <th>Created At</th>
                <th style={{ width: 120 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} cols={5} />)
              ) : !filteredGroups || filteredGroups.length === 0 ? (
                <tr>
                  <td colSpan={5}>
                    <EmptyState
                      icon={<FolderLock size={32} />}
                      title={activeTab === 'my-groups' ? 'No groups assigned' : 'No groups configured'}
                      subtitle={activeTab === 'my-groups' ? 'You are not a member of any access group.' : 'Create groups to assemble roles for collections of operators.'}
                    />
                  </td>
                </tr>
              ) : (
                filteredGroups.map((g) => (
                  <tr key={g.id}>
                    <td>#{g.id}</td>
                    <td style={{ fontWeight: 'var(--font-medium)', color: 'var(--text-primary)' }}>{g.name}</td>
                    <td>{g.description || '—'}</td>
                    <td>{g.created ? new Date(g.created).toLocaleDateString() : '—'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'center' }}>
                        <Button size="sm" variant="ghost" onClick={() => navigate(`/groups/${g.id}`)} icon>
                          <ChevronRight size={16} />
                        </Button>
                        {isAdmin && (
                          <>
                            <Button size="sm" variant="ghost" onClick={() => openEditModal(g)} icon>
                              <Edit2 size={16} />
                            </Button>
                            <Button size="sm" variant="ghost" onClick={() => openDeleteModal(g)} icon>
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
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create User Group">
        <form className="auth-form" onSubmit={handleSubmitCreate(handleCreate)}>
          <Input
            label="Group Name"
            type="text"
            placeholder="e.g. Finance Operators"
            error={errorsCreate.name?.message}
            {...registerCreate('name')}
          />
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-input"
              rows={4}
              placeholder="Provide a description explaining the purpose of this group..."
              {...registerCreate('description')}
            />
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <Button type="button" variant="secondary" onClick={() => setIsCreateOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={createMutation.isPending}>
              Create Group
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Modify User Group">
        <form className="auth-form" onSubmit={handleSubmitEdit(handleEdit)}>
          <Input
            label="Group Name"
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
        onConfirm={() => deleteMutation.mutate(selectedGroup?.id)}
        loading={deleteMutation.isPending}
        title="Delete User Group?"
        message={`Are you sure you want to delete the group "${selectedGroup?.name}"? This operation cannot be undone.`}
      />
    </div>
  );
}
