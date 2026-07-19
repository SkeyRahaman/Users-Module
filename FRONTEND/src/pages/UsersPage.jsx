import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import toast from 'react-hot-toast';
import {
  Search,
  Plus,
  ArrowUpDown,
  Check,
  X,
  Lock,
  UserCheck,
  UserX,
  MoreVertical,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';
import { usePermission } from '../hooks/usePermission.js';
import { PERMISSIONS } from '../utils/constants.js';
import { usersApi } from '../api/users.js';
import { groupsApi } from '../api/groups.js';
import { rolesApi } from '../api/roles.js';
import { registerSchema } from '../utils/validators.js';
import { SkeletonRow } from '../components/ui/Skeleton.jsx';
import Pagination from '../components/ui/Pagination.jsx';
import Modal from '../components/ui/Modal.jsx';
import Input from '../components/ui/Input.jsx';
import Button from '../components/ui/Button.jsx';
import SearchBar from '../components/ui/SearchBar.jsx';
import EmptyState from '../components/ui/EmptyState.jsx';
import Dropdown, { DropdownItem } from '../components/ui/Dropdown.jsx';
import Can from '../components/ui/Can.jsx';

export default function UsersPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { hasPermission } = usePermission();

  // Filters & State
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');
  const [groupFilter, setGroupFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [sortBy, setSortBy] = useState('created');
  const [sortOrder, setSortOrder] = useState('desc');

  // Multi-select / Bulk states
  const [selectedIds, setSelectedIds] = useState([]);
  const [bulkLoading, setBulkLoading] = useState(false);

  // Modals state
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // Fetch roles and groups for filter dropdowns
  const { data: roles } = useQuery({ queryKey: ['roles', 'filter'], queryFn: rolesApi.getAllRoles });
  const { data: groups } = useQuery({ queryKey: ['groups', 'filter'], queryFn: groupsApi.getAllGroups });

  // Query Parameters mapping
  const statusParam = statusFilter === 'all' ? undefined : statusFilter === 'active';
  const roleParam = roleFilter === 'all' ? undefined : roleFilter;
  const groupParam = groupFilter === 'all' ? undefined : groupFilter;

  // Main Users query
  const { data: usersResponse, isLoading } = useQuery({
    queryKey: ['users', 'list', { page, limit, sort_by: sortBy, sort_order: sortOrder, status: statusParam, role: roleParam, group: groupParam, search }],
    queryFn: () => usersApi.getAllUsers({
      page,
      limit,
      sort_by: sortBy,
      sort_order: sortOrder,
      status: statusParam,
      role: roleParam,
      group: groupParam,
      search: search || undefined
    }),
  });

  // User Actions mutations
  const activateMutation = useMutation({
    mutationFn: usersApi.activateUser,
    onSuccess: (_, userId) => {
      qc.invalidateQueries({ queryKey: ['users'] });
      toast.success(`User activated successfully.`);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to activate user.');
    }
  });

  const deactivateMutation = useMutation({
    mutationFn: ({ userId }) => usersApi.deactivateUser(userId),
    onSuccess: (_, { userId }) => {
      qc.invalidateQueries({ queryKey: ['users'] });
      toast.success(`User deactivated successfully.`);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to deactivate user.');
    }
  });

  const createMutation = useMutation({
    mutationFn: usersApi.createUser,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users'] });
      toast.success('User account registered successfully.');
      setIsCreateOpen(false);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Registration failed.');
    }
  });

  // Create Form handler
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const handleCreateSubmit = (data) => {
    const { confirmPassword, ...submitData } = data;
    createMutation.mutate(submitData);
  };

  // Sort helper
  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  // Bulk operation actions
  const handleSelectAll = (e) => {
    if (e.target.checked && usersResponse?.users) {
      setSelectedIds(usersResponse.users.map((u) => u.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectRow = (id, checked) => {
    if (checked) {
      setSelectedIds([...selectedIds, id]);
    } else {
      setSelectedIds(selectedIds.filter((rowId) => rowId !== id));
    }
  };

  const handleBulkActivate = async () => {
    setBulkLoading(true);
    try {
      await Promise.allSettled(selectedIds.map((id) => usersApi.activateUser(id)));
      toast.success('Selected users activated.');
      setSelectedIds([]);
      qc.invalidateQueries({ queryKey: ['users'] });
    } catch {
      toast.error('Some activation requests failed.');
    } finally {
      setBulkLoading(false);
    }
  };

  const handleBulkDeactivate = async () => {
    setBulkLoading(true);
    try {
      await Promise.allSettled(selectedIds.map((id) => usersApi.deactivateUser(id)));
      toast.success('Selected users deactivated.');
      setSelectedIds([]);
      qc.invalidateQueries({ queryKey: ['users'] });
    } catch {
      toast.error('Some deactivation requests failed.');
    } finally {
      setBulkLoading(false);
    }
  };

  return (
    <div className="animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="page-header">
        <div className="page-header-info">
          <h1 className="page-title">User Accounts</h1>
          <p className="page-subtitle">Inspect directory details, update status levels, and manage membership details</p>
        </div>
        <div className="page-actions">
          <Button onClick={() => { reset(); setIsCreateOpen(true); }} style={{ gap: '0.4rem' }}>
            <Plus size={16} /> Register User
          </Button>
        </div>
      </div>

      {/* Toolbar / Filters */}
      <div className="card" style={{ padding: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <SearchBar value={search} onChange={setSearch} placeholder="Search by name, email, username..." />

          <select
            className="form-input"
            style={{ width: 'auto', minWidth: 120 }}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Statuses</option>
            <option value="active">Active Only</option>
            <option value="inactive">Inactive Only</option>
          </select>

          <select
            className="form-input"
            style={{ width: 'auto', minWidth: 140 }}
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
          >
            <option value="all">All Roles</option>
            {roles?.map((r) => (
              <option key={r.id} value={r.name}>{r.name}</option>
            ))}
          </select>

          <select
            className="form-input"
            style={{ width: 'auto', minWidth: 140 }}
            value={groupFilter}
            onChange={(e) => setGroupFilter(e.target.value)}
          >
            <option value="all">All Groups</option>
            {groups?.map((g) => (
              <option key={g.id} value={g.name}>{g.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Bulk Action Bar */}
      {selectedIds.length > 0 && (
        <div className="bulk-action-bar">
          <div className="bulk-action-bar-left">
            {selectedIds.length} user{selectedIds.length > 1 ? 's' : ''} selected
          </div>
          <div className="bulk-action-bar-right">
            <Can permission={PERMISSIONS.ACTIVATE_USER}>
              <Button size="sm" variant="success" onClick={handleBulkActivate} loading={bulkLoading}>
                Activate Selected
              </Button>
            </Can>
            <Can permission={PERMISSIONS.DEACTIVATE_USER}>
              <Button size="sm" variant="danger" onClick={handleBulkDeactivate} loading={bulkLoading}>
                Deactivate Selected
              </Button>
            </Can>
            <Button size="sm" variant="secondary" onClick={() => setSelectedIds([])} disabled={bulkLoading}>
              Clear
            </Button>
          </div>
        </div>
      )}

      {/* Data Table */}
      <div className="table-container">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 40 }}>
                  <input
                    type="checkbox"
                    className="table-checkbox"
                    onChange={handleSelectAll}
                    checked={
                      usersResponse?.users &&
                      usersResponse.users.length > 0 &&
                      selectedIds.length === usersResponse.users.length
                    }
                  />
                </th>
                <th className="sortable" onClick={() => handleSort('username')}>
                  <div className="th-content">Username <ArrowUpDown size={12} /></div>
                </th>
                <th>Full Name</th>
                <th className="sortable" onClick={() => handleSort('email')}>
                  <div className="th-content">Email <ArrowUpDown size={12} /></div>
                </th>
                <th>Status</th>
                <th>Registered</th>
                <th style={{ width: 80 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: limit }).map((_, i) => <SkeletonRow key={i} cols={7} />)
              ) : !usersResponse?.users || usersResponse.users.length === 0 ? (
                <tr>
                  <td colSpan={7}>
                    <EmptyState title="No users found" subtitle="Try clearing your search terms or filters." />
                  </td>
                </tr>
              ) : (
                usersResponse.users.map((u) => {
                  const isChecked = selectedIds.includes(u.id);
                  return (
                    <tr key={u.id} className={isChecked ? 'selected' : ''}>
                      <td>
                        <input
                          type="checkbox"
                          className="table-checkbox"
                          checked={isChecked}
                          onChange={(e) => handleSelectRow(u.id, e.target.checked)}
                        />
                      </td>
                      <td style={{ fontWeight: 'var(--font-medium)', color: 'var(--text-primary)' }}>
                        @{u.username}
                      </td>
                      <td>{u.firstname} {u.lastname}</td>
                      <td>{u.email}</td>
                      <td>
                        <span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`} dot>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>{u.created ? new Date(u.created).toLocaleDateString() : '—'}</td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'center' }}>
                          <Button size="sm" variant="ghost" onClick={() => navigate(`/users/${u.id}`)} icon>
                            <ChevronRight size={16} />
                          </Button>
                          <Dropdown
                            trigger={
                              <Button size="sm" variant="ghost" icon>
                                <MoreVertical size={16} />
                              </Button>
                            }
                          >
                            <DropdownItem onClick={() => navigate(`/users/${u.id}`)}>
                              View Profile
                            </DropdownItem>
                            
                            <Can permission={PERMISSIONS.ACTIVATE_USER}>
                              {!u.is_active && (
                                <DropdownItem onClick={() => activateMutation.mutate(u.id)}>
                                  Activate
                                </DropdownItem>
                              )}
                            </Can>
                            
                            <Can permission={PERMISSIONS.DEACTIVATE_USER}>
                              {u.is_active && (
                                <DropdownItem onClick={() => deactivateMutation.mutate({ userId: u.id })} danger>
                                  Deactivate
                                </DropdownItem>
                              )}
                            </Can>
                          </Dropdown>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {usersResponse && (
          <Pagination
            page={page}
            limit={limit}
            total={usersResponse.total}
            onPageChange={setPage}
            onLimitChange={setLimit}
          />
        )}
      </div>

      {/* Create Modal */}
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Register User Account">
        <form className="auth-form" onSubmit={handleSubmit(handleCreateSubmit)}>
          <div className="auth-form-row">
            <Input
              label="First Name"
              type="text"
              error={errors.firstname?.message}
              {...register('firstname')}
            />
            <Input
              label="Last Name"
              type="text"
              error={errors.lastname?.message}
              {...register('lastname')}
            />
          </div>

          <Input
            label="Middle Name"
            type="text"
            error={errors.middlename?.message}
            {...register('middlename')}
          />

          <Input
            label="Email Address"
            type="email"
            placeholder="e.g. name@example.com"
            error={errors.email?.message}
            {...register('email')}
          />

          <Input
            label="Username"
            type="text"
            placeholder="e.g. jane_doe"
            error={errors.username?.message}
            {...register('username')}
          />

          <Input
            label="Password"
            type="password"
            placeholder="At least 8 characters"
            error={errors.password?.message}
            {...register('password')}
          />

          <Input
            label="Confirm Password"
            type="password"
            placeholder="At least 8 characters"
            error={errors.confirmPassword?.message}
            {...register('confirmPassword')}
          />

          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <Button type="button" variant="secondary" onClick={() => setIsCreateOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={createMutation.isPending}>
              Create Account
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
