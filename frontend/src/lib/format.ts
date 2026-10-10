export function formatDateTime(value?: string | null): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatBytes(size?: number | null): string {
  if (size == null || Number.isNaN(size)) return '—';
  if (size < 1024) return `${size} B`;
  return `${(size / 1024).toFixed(1)} KB`;
}

export function labelStatus(value?: string | null): string {
  if (!value) return 'Unknown';
  return value.replace(/_/g, ' ');
}

export function truncate(value?: string | null, length = 80): string {
  if (!value) return '';
  return value.length > length ? `${value.slice(0, length)}…` : value;
}
