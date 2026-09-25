import type { ReactNode } from 'react'

interface StatCardProps {
  label: string
  value: ReactNode
  hint?: string
  tone?: 'default' | 'success' | 'danger' | 'warning'
}

export function StatCard({ label, value, hint, tone = 'default' }: StatCardProps) {
  return (
    <article className={`stat-card stat-${tone}`}>
      <p className="stat-label">{label}</p>
      <strong className="stat-value">{value}</strong>
      {hint && <span className="stat-hint">{hint}</span>}
    </article>
  )
}
