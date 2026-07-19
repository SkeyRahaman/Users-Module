import { forwardRef, useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

const Input = forwardRef(function Input(
  { label, error, hint, iconLeft, iconRight, className = '', type = 'text', ...props },
  ref
) {
  const [showPassword, setShowPassword] = useState(false);

  const isPassword = type === 'password';
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;

  const handleTogglePassword = (e) => {
    e.preventDefault();
    setShowPassword((prev) => !prev);
  };

  const inputClass = [
    'form-input',
    iconLeft ? 'has-icon-left' : '',
    iconRight || isPassword ? 'has-icon-right' : '',
    error ? 'error' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className="form-group">
      {label && <label className="form-label">{label}</label>}
      <div className="input-wrapper">
        {iconLeft && <span className="input-icon-left">{iconLeft}</span>}
        <input ref={ref} type={inputType} className={inputClass} {...props} />
        {isPassword ? (
          <button
            type="button"
            className="input-icon-right"
            onClick={handleTogglePassword}
            style={{
              background: 'none',
              border: 'none',
              padding: 0,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-secondary)',
            }}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        ) : (
          iconRight && <span className="input-icon-right">{iconRight}</span>
        )}
      </div>
      {error && <span className="form-error">{error}</span>}
      {hint && !error && <span className="form-hint">{hint}</span>}
    </div>
  );
});

export default Input;
