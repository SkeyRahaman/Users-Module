import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { UserPlus, User as UserIcon, Mail, KeyRound, Settings2, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../hooks/useAuth.js';
import { registerSchema } from '../utils/validators.js';
import Input from '../components/ui/Input.jsx';
import Button from '../components/ui/Button.jsx';

export default function RegisterPage() {
  const { register: authRegister } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      // Exclude confirmPassword
      const { confirmPassword, ...submitData } = data;
      await authRegister(submitData);
      setIsSuccess(true);
      toast.success('Registration successful!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed. Try another username/email.');
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
          <h2 className="auth-hero-title">Create Admin Console Account</h2>
          <p className="auth-hero-subtitle">
            Sign up to get a direct administrative account and begin creating custom groups, roles, and permissions configuration models.
          </p>
        </div>
      </div>

      {/* Right Panel */}
      <div className="auth-form-panel">
        <div className="auth-form-card animate-slide-up">
          {isSuccess ? (
            <div className="auth-success-card animate-scale-in">
              <div className="auth-success-icon">
                <CheckCircle2 size={36} />
              </div>
              <h1 className="auth-form-title">Account Created!</h1>
              <p className="auth-form-subtitle" style={{ maxWidth: 320, margin: '0 auto' }}>
                Your administrator account has been successfully created. You can now log in.
              </p>
              <Button onClick={() => navigate('/login')} className="auth-submit-btn" style={{ maxWidth: 200 }}>
                Return to Login
              </Button>
            </div>
          ) : (
            <>
              <div className="auth-form-header">
                <h1 className="auth-form-title">Get Started</h1>
                <p className="auth-form-subtitle">Create a new operator account for the management console</p>
              </div>

              <form className="auth-form" onSubmit={handleSubmit(onSubmit)}>
                <div className="auth-form-row">
                  <Input
                    label="First Name"
                    type="text"
                    placeholder="Enter your first name"
                    error={errors.firstname?.message}
                    {...register('firstname')}
                  />
                  <Input
                    label="Last Name"
                    type="text"
                    placeholder="Enter your last name"
                    error={errors.lastname?.message}
                    {...register('lastname')}
                  />
                </div>

                <Input
                  label="Middle Name (Optional)"
                  type="text"
                  placeholder="Enter your middle name"
                  error={errors.middlename?.message}
                  {...register('middlename')}
                />

                <Input
                  label="Email Address"
                  type="email"
                  placeholder="Enter your email address"
                  iconLeft={<Mail size={18} />}
                  error={errors.email?.message}
                  {...register('email')}
                />

                <Input
                  label="Username"
                  type="text"
                  placeholder="Choose a username"
                  iconLeft={<UserIcon size={18} />}
                  error={errors.username?.message}
                  {...register('username')}
                />

                <Input
                  label="Password"
                  type="password"
                  placeholder="Create a password"
                  iconLeft={<KeyRound size={18} />}
                  error={errors.password?.message}
                  {...register('password')}
                />

                <Input
                  label="Confirm Password"
                  type="password"
                  placeholder="Confirm your password"
                  iconLeft={<KeyRound size={18} />}
                  error={errors.confirmPassword?.message}
                  {...register('confirmPassword')}
                />

                <Button type="submit" className="auth-submit-btn" loading={loading}>
                  <UserPlus size={18} /> Create Account
                </Button>
              </form>

              <p className="auth-footer-text">
                Already have an account? <Link to="/login" className="auth-form-link">Sign In</Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
