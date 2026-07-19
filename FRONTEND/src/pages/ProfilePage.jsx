import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { User, ShieldCheck, Mail, LogOut, Trash2, KeyRound } from 'lucide-react';
import { useAuth } from '../hooks/useAuth.js';
import { usePermission } from '../hooks/usePermission.js';
import { usersApi } from '../api/users.js';
import { userUpdateSchema } from '../utils/validators.js';
import Avatar from '../components/ui/Avatar.jsx';
import Button from '../components/ui/Button.jsx';
import Input from '../components/ui/Input.jsx';
import ConfirmDialog from '../components/ui/ConfirmDialog.jsx';

export default function ProfilePage() {
  const { user, logout, updateUser } = useAuth();
  const { permissions } = usePermission();
  const qc = useQueryClient();
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  // Fetch current user details
  const { data: me, isLoading } = useQuery({
    queryKey: ['users', 'me'],
    queryFn: usersApi.getMe,
    initialData: user,
  });

  const updateMutation = useMutation({
    mutationFn: usersApi.updateMe,
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ['users', 'me'] });
      updateUser(updated);
      toast.success('Profile updated successfully.');
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to update profile.');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: usersApi.deleteMe,
    onSuccess: () => {
      toast.success('Your account has been deleted.');
      logout();
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to delete account.');
    }
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(userUpdateSchema),
    defaultValues: {
      firstname: me?.firstname || '',
      middlename: me?.middlename || '',
      lastname: me?.lastname || '',
      email: me?.email || '',
      username: me?.username || '',
    }
  });

  const onSubmit = (data) => {
    const updateData = {};
    Object.keys(data).forEach((key) => {
      if (data[key] !== '') updateData[key] = data[key];
    });
    updateMutation.mutate(updateData);
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
        <div className="btn-spinner" style={{ width: 40, height: 40, borderTopColor: 'var(--accent)' }} />
      </div>
    );
  }

  return (
    <div className="animate-slide-up profile-page-root">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-info">
          <h1 className="page-title">My Profile</h1>
          <p className="page-subtitle">Manage your personal settings and security authorization levels</p>
        </div>
      </div>

      {/* Profile Hero Card — avatar + name + sign out */}
      <div className="card profile-hero-card">
        <div className="profile-hero-inner">
          <Avatar user={me} size="xl" />
          <div className="profile-hero-info">
            <h2 className="profile-hero-name">{me?.firstname} {me?.lastname}</h2>
            <p className="profile-hero-username">@{me?.username}</p>
            <p className="profile-hero-email">{me?.email}</p>
          </div>
          <div className="profile-hero-actions">
            <Button variant="outline" onClick={logout} className="profile-signout-btn">
              <LogOut size={16} /> Sign Out
            </Button>
          </div>
        </div>
      </div>

      {/* Main 2-column layout (stacks on mobile) */}
      <div className="profile-layout-grid">
        {/* Left: Edit Form */}
        <div className="card profile-form-card">
          <h2 className="card-title" style={{ marginBottom: '1.5rem' }}>Profile Information</h2>
          <form className="auth-form" onSubmit={handleSubmit(onSubmit)}>
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
              iconLeft={<Mail size={18} />}
              error={errors.email?.message}
              {...register('email')}
            />

            <Input
              label="Username"
              type="text"
              error={errors.username?.message}
              {...register('username')}
            />

            <Input
              label="New Password"
              type="password"
              placeholder="Leave blank to keep current password"
              iconLeft={<KeyRound size={18} />}
              error={errors.password?.message}
              {...register('password')}
            />

            <div className="profile-form-submit">
              <Button type="submit" loading={updateMutation.isPending}>
                Save Changes
              </Button>
            </div>
          </form>
        </div>

        {/* Right: Scopes + Danger Zone */}
        <div className="profile-sidebar">
          {/* Resolved Scopes */}
          <div className="card">
            <h3 className="card-title" style={{ fontSize: '0.95rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <ShieldCheck size={18} /> Resolved Scopes
            </h3>
            {permissions.size === 0 ? (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No direct scopes assigned.</p>
            ) : (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {Array.from(permissions).map((p) => (
                  <span className="badge badge-violet" key={p} style={{ fontSize: '0.72rem' }}>{p}</span>
                ))}
              </div>
            )}
          </div>

          {/* Danger Zone */}
          <div className="danger-zone">
            <h3 className="danger-zone-title">Danger Zone</h3>
            <p className="danger-zone-desc">Permanently remove your administrative operator profile and credentials from this directory.</p>
            <Button variant="danger" size="sm" onClick={() => setIsDeleteOpen(true)} style={{ width: '100%', gap: '0.5rem' }}>
              <Trash2 size={16} /> Delete Account
            </Button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        loading={deleteMutation.isPending}
        title="Delete Operator Profile?"
        message="Are you sure you want to permanently delete your account? This action is irreversible and will sign you out."
      />
    </div>
  );
}
