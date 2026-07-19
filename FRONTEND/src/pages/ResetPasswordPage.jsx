import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { KeyRound, ArrowLeft, Settings2, CheckCircle2, Ticket } from 'lucide-react';
import { authApi } from '../api/auth.js';
import { resetPasswordSchema } from '../utils/validators.js';
import Input from '../components/ui/Input.jsx';
import Button from '../components/ui/Button.jsx';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const tokenParam = searchParams.get('token') || '';

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      token: tokenParam,
    },
  });

  // Auto-fill token from search params if it changes
  useEffect(() => {
    if (tokenParam) {
      setValue('token', tokenParam);
    }
  }, [tokenParam, setValue]);

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await authApi.confirmPasswordReset({
        token: data.token,
        new_password: data.new_password,
      });
      setIsSuccess(true);
      toast.success('Password reset successfully!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Token is invalid or has expired.');
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
            <span className="auth-logo-text">AuthConsole</span>
          </div>
          <h2 className="auth-hero-title">Reset Your Credentials</h2>
          <p className="auth-hero-subtitle">
            Create a strong new password containing combinations of numbers, characters, and capital letters to restore console access.
          </p>
        </div>
      </div>

      {/* Right Panel */}
      <div className="auth-form-panel">
        <div className="auth-form-card animate-slide-up">
          <Link to="/login" className="auth-form-link" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', marginBottom: '2rem' }}>
            <ArrowLeft size={16} /> Back to Sign In
          </Link>

          {isSuccess ? (
            <div className="auth-success-card animate-scale-in">
              <div className="auth-success-icon">
                <CheckCircle2 size={36} />
              </div>
              <h1 className="auth-form-title">Password Reset</h1>
              <p className="auth-form-subtitle" style={{ maxWidth: 320, margin: '0 auto' }}>
                Your credentials have been successfully updated. You can now log in with your new password.
              </p>
              <Button onClick={() => navigate('/login')} className="auth-submit-btn" style={{ maxWidth: 200 }}>
                Sign In Now
              </Button>
            </div>
          ) : (
            <>
              <div className="auth-form-header">
                <h1 className="auth-form-title">Reset Password</h1>
                <p className="auth-form-subtitle">Enter your reset token and your new chosen password</p>
              </div>

              <form className="auth-form" onSubmit={handleSubmit(onSubmit)}>
                <Input
                  label="Reset Token"
                  type="text"
                  placeholder="Paste your reset token from the email"
                  iconLeft={<Ticket size={18} />}
                  error={errors.token?.message}
                  {...register('token')}
                />

                <Input
                  label="New Password"
                  type="password"
                  placeholder="••••••••"
                  iconLeft={<KeyRound size={18} />}
                  error={errors.new_password?.message}
                  {...register('new_password')}
                />

                <Input
                  label="Confirm New Password"
                  type="password"
                  placeholder="••••••••"
                  iconLeft={<KeyRound size={18} />}
                  error={errors.confirmPassword?.message}
                  {...register('confirmPassword')}
                />

                <Button type="submit" className="auth-submit-btn" loading={loading}>
                  Save & Reset Password
                </Button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
