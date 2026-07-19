export default function EmptyState({ icon, title, subtitle, action }) {
  return (
    <div className="empty-state">
      {icon && (
        <div className="empty-state-icon">
          {icon}
        </div>
      )}
      {title && <p className="empty-state-title">{title}</p>}
      {subtitle && <p className="empty-state-subtitle">{subtitle}</p>}
      {action && action}
    </div>
  );
}
