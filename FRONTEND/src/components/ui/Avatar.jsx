import { getUserInitials } from '../../utils/formatters.js';

export default function Avatar({ user, size = '', className = '' }) {
  const initials = getUserInitials(user);
  const sizeClass = size ? `avatar-${size}` : '';

  // Generate a consistent gradient based on the user's name
  const hue = (user?.username ?? 'X')
    .split('')
    .reduce((acc, ch) => acc + ch.charCodeAt(0), 0) % 360;
  const style = {
    background: `linear-gradient(135deg, hsl(${hue}, 65%, 55%), hsl(${(hue + 60) % 360}, 65%, 45%))`,
  };

  return (
    <div className={`avatar ${sizeClass} ${className}`.trim()} style={style} title={user?.username}>
      {initials}
    </div>
  );
}
