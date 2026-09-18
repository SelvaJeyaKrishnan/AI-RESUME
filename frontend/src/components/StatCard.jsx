import clsx from 'clsx'

export default function StatCard({ label, value, hint, tone = 'default' }) {
  const toneClasses = {
    default: 'text-ink dark:text-paper',
    amber: 'text-amber-600 dark:text-amber-400',
    sage: 'text-sage-600 dark:text-sage-500',
  }
  return (
    <div className="card p-5">
      <p className="label-eyebrow mb-2">{label}</p>
      <p className={clsx('font-display text-3xl', toneClasses[tone])}>{value}</p>
      {hint && <p className="text-xs text-ink/50 dark:text-paper/50 mt-1">{hint}</p>}
    </div>
  )
}
