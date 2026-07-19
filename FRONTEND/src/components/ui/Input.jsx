import { forwardRef } from 'react';

const Input = forwardRef(function Input(
  { label, error, hint, iconLeft, iconRight, className = '', ...props },
  ref
) {
  const inputClass = [
    'form-input',
    iconLeft ? 'has-icon-left' : '',
    iconRight ? 'has-icon-right' : '',
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
        <input ref={ref} className={inputClass} {...props} />
        {iconRight && <span className="input-icon-right">{iconRight}</span>}
      </div>
      {error && <span className="form-error">{error}</span>}
      {hint && !error && <span className="form-hint">{hint}</span>}
    </div>
  );
});

export default Input;
