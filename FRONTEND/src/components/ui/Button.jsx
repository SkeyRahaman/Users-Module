export default function Button({
  children,
  variant = 'primary',
  size = '',
  icon = false,
  loading = false,
  className = '',
  ...props
}) {
  const classes = [
    'btn',
    `btn-${variant}`,
    size ? `btn-${size}` : '',
    icon ? 'btn-icon' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={classes} disabled={loading || props.disabled} {...props}>
      {loading ? (
        <>
          <span className="btn-spinner" />
          {typeof children === 'string' ? '' : children}
        </>
      ) : (
        children
      )}
    </button>
  );
}
