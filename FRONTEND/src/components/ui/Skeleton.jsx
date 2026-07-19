export function Skeleton({ width, height = 16, className = '' }) {
  return (
    <div
      className={`skeleton-cell ${className}`}
      style={{ width: width ?? '100%', height }}
    />
  );
}

export function SkeletonRow({ cols = 5 }) {
  return (
    <tr className="skeleton-row">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i}>
          <Skeleton width={i === 0 ? 32 : undefined} height={i === 0 ? 32 : 14} />
        </td>
      ))}
    </tr>
  );
}

export function SkeletonCard() {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Skeleton width="60%" height={20} />
      <Skeleton height={14} />
      <Skeleton width="80%" height={14} />
    </div>
  );
}
