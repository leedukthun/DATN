export function formatDate(value: string): string {
  if (!value) return '—'
  const [year, month, day] = value.slice(0, 10).split('-')
  return `${day}/${month}/${year}`
}

export function formatDateTime(value?: string | null): string {
  if (!value) return '—'
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function formatTime(value: string): string {
  return value?.slice(0, 5) || '—'
}

export function formatPercent(value: number): string {
  return `${Number(value || 0).toFixed(2)}%`
}

export function formatTimestamp(seconds?: number | null): string {
  if (seconds === null || seconds === undefined) return 'Ảnh tĩnh'
  const minutes = Math.floor(seconds / 60)
  const remain = seconds - minutes * 60
  return `${String(minutes).padStart(2, '0')}:${remain.toFixed(2).padStart(5, '0')}`
}

export function fileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

export function todayIso(): string {
  const now = new Date()
  const offset = now.getTimezoneOffset()
  return new Date(now.getTime() - offset * 60_000).toISOString().slice(0, 10)
}
