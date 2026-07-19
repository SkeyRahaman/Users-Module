import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect, useRef, useCallback } from 'react';
import toast from 'react-hot-toast';
import { LogIn, KeyRound, User as UserIcon, Settings2, ShieldCheck } from 'lucide-react';
import { useAuth } from '../hooks/useAuth.js';
import { loginSchema } from '../utils/validators.js';
import Input from '../components/ui/Input.jsx';
import Button from '../components/ui/Button.jsx';
import MobileAuthHeader from '../components/auth/MobileAuthHeader.jsx';

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const autoLoginFired = useRef(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const from = location.state?.from?.pathname || '/dashboard';

  const doAutoLogin = useCallback(async () => {
    try {
      await login({ username: 'admin', password: 'adminpassword' });
      // Set flag so AppLayout renders the DemoBanner after redirect
      sessionStorage.setItem('show_demo_banner', 'true');
      navigate(from, { replace: true });
    } catch {
      // Backend might be cold-starting; silently fall back to manual login
    }
  }, [login, navigate, from]);

  // Auto-login as admin on first render (demo mode)
  useEffect(() => {
    if (autoLoginFired.current || isAuthenticated) return;
    autoLoginFired.current = true;
    doAutoLogin();
  }, [isAuthenticated, doAutoLogin]);

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await login(data);
      toast.success('Welcome back!');
      navigate(from, { replace: true });
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid username or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout">
      {/* Left Panel */}
      <div className="auth-hero">
        <div className="auth-hero-decor auth-hero-decor-1" />
        <div className="auth-hero-decor auth-hero-decor-2" />
        
        <div className="auth-hero-content">
          <div className="auth-logo">
            <div className="auth-logo-mark">
              <Settings2 size={28} />
            </div>
            <span className="auth-logo-text">Users_Module</span>
          </div>
          <h2 className="auth-hero-title">Identity &amp; Access Management</h2>
          <p className="auth-hero-subtitle">
            Securely configure user lifecycles, assign granular role permissions, and track active sessions in real-time.
          </p>

          <ul className="auth-feature-list">
            <li className="auth-feature-item">
              <div className="auth-feature-icon"><ShieldCheck size={16} /></div>
              <span>Role-Based Access Controls (RBAC)</span>
            </li>
            <li className="auth-feature-item">
              <div className="auth-feature-icon"><ShieldCheck size={16} /></div>
              <span>Deduplicated User Groups Mapping</span>
            </li>
            <li className="auth-feature-item">
              <div className="auth-feature-icon"><ShieldCheck size={16} /></div>
              <span>Detailed User Audit Log Timelines</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Right Panel */}
      <div className="auth-form-panel">
        <MobileAuthHeader />

        <div className="auth-form-card animate-slide-up">
          <div className="auth-form-header">
            <h1 className="auth-form-title">Welcome back</h1>
            <p className="auth-form-subtitle">Please enter your credentials to access the console</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit(onSubmit)}>
            <Input
              label="Username"
              type="text"
              placeholder="Enter your username"
              iconLeft={<UserIcon size={18} />}
              error={errors.username?.message}
              {...register('username')}
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              iconLeft={<KeyRound size={18} />}
              error={errors.password?.message}
              {...register('password')}
            />

            <div className="auth-form-actions">
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-secondary)' }}>
                <input type="checkbox" className="table-checkbox" style={{ width: 15, height: 15 }} />
                <span>Keep me signed in</span>
              </label>
              <Link to="/forgot-password" className="auth-form-link">Forgot password?</Link>
            </div>

            <Button type="submit" className="auth-submit-btn" loading={loading}>
              <LogIn size={18} /> Sign In
            </Button>
          </form>

          <p className="auth-footer-text">
            Don't have an account? <Link to="/register" className="auth-form-link">Sign Up</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
