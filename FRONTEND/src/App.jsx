import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// Context Providers
import { ThemeProvider } from './context/ThemeContext.jsx';
import { AuthProvider } from './context/AuthContext.jsx';
import { PermissionProvider } from './context/PermissionContext.jsx';

// Layout Components
import AppLayout from './components/layout/AppLayout.jsx';
import ProtectedRoute from './components/layout/ProtectedRoute.jsx';

// Pages
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import ForgotPasswordPage from './pages/ForgotPasswordPage.jsx';
import ResetPasswordPage from './pages/ResetPasswordPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import UsersPage from './pages/UsersPage.jsx';
import UserDetailPage from './pages/UserDetailPage.jsx';
import GroupsPage from './pages/GroupsPage.jsx';
import GroupDetailPage from './pages/GroupDetailPage.jsx';
import RolesPage from './pages/RolesPage.jsx';
import RoleDetailPage from './pages/RoleDetailPage.jsx';
import PermissionsPage from './pages/PermissionsPage.jsx';
import PermissionDetailPage from './pages/PermissionDetailPage.jsx';
import ProfilePage from './pages/ProfilePage.jsx';
import UnauthorizedPage from './pages/UnauthorizedPage.jsx';
import NotFoundPage from './pages/NotFoundPage.jsx';

// Constants
import { PERMISSIONS } from './utils/constants.js';

// Setup TanStack Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <PermissionProvider>
            <BrowserRouter basename="/Users-Module">
              <Routes>
                {/* Public Auth Routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />

                {/* Gated Application Console Routes */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <AppLayout />
                    </ProtectedRoute>
                  }
                >
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  <Route path="dashboard" element={<DashboardPage />} />
                  
                  {/* Gated Users Directory */}
                  <Route
                    path="users"
                    element={
                      <ProtectedRoute requiredPermission={PERMISSIONS.SEARCH_USER}>
                        <UsersPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="users/:id"
                    element={
                      <ProtectedRoute requiredPermission={PERMISSIONS.SEARCH_USER}>
                        <UserDetailPage />
                      </ProtectedRoute>
                    }
                  />

                  {/* Groups Directory */}
                  <Route path="groups" element={<GroupsPage />} />
                  <Route path="groups/:id" element={<GroupDetailPage />} />

                  {/* Roles Directory */}
                  <Route path="roles" element={<RolesPage />} />
                  <Route path="roles/:id" element={<RoleDetailPage />} />

                  {/* Permissions Scopes Directory */}
                  <Route path="permissions" element={<PermissionsPage />} />
                  <Route path="permissions/:id" element={<PermissionDetailPage />} />

                  {/* General Profile Page */}
                  <Route path="profile" element={<ProfilePage />} />

                  {/* Access Restricted Errors */}
                  <Route path="unauthorized" element={<UnauthorizedPage />} />
                </Route>

                {/* 404 handler */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </BrowserRouter>

            {/* Notification Toasts setup */}
            <Toaster
              position="top-right"
              toastOptions={{
                className: '',
                style: {
                  background: 'var(--bg-secondary)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.9rem',
                },
              }}
            />
          </PermissionProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
