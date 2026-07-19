import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { Mail, ArrowLeft, Settings2, CheckCircle2 } from 'lucide-react';
import { authApi } from '../api/auth.js';
import { forgotPasswordSchema } from '../utils/validators.js';
import Input from '../components/ui/Input.jsx';
import Button from '../components/ui/Button.jsx';

export default function ForgotPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await authApi.requestPasswordReset(data);
      setIsSuccess(true);
      toast.success('Reset email requested!');
    } catch {
      // Return success regardless to prevent user enumeration
      setIsSuccess(true);
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
          <h2 className="auth-hero-title">Reset Administrator Password</h2>
          <p className="auth-hero-subtitle">
            Enter your email to receive a secure token to reset your password and restore console access.
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
              <h1 className="auth-form-title">Request Sent</h1>
              <p className="auth-form-subtitle" style={{ maxWidth: 340, margin: '0 auto' }}>
                If your email address is registered on our system, you will receive a password reset token email shortly.
              </p>
            </div>
          ) : (
            <>
              <div className="auth-form-header">
                <h1 className="auth-form-title">Forgot Password</h1>
                <p className="auth-form-subtitle">Enter your email and we'll send a password recovery request</p>
              </div>

              <form className="auth-form" onSubmit={handleSubmit(onSubmit)}>
                <Input
                  label="Email Address"
                  type="email"
                  placeholder="name@example.com"
                  iconLeft={<Mail size={18} />}
                  error={errors.email?.message}
                  {...register('email')}
                />

                <Button type="submit" className="auth-submit-btn" loading={loading}>
                  Send Recovery Link
                </Button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
