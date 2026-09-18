import clsx from 'clsx'

const STYLES = {
  'Strong Match': 'bg-sage-100 text-sage-600 dark:bg-sage-500/20 dark:text-sage-100',
  'Good Match': 'bg-amber-400/20 text-amber-600 dark:text-amber-400',
  'Potential Match': 'bg-brand-100 text-brand-600 dark:bg-brand-500/20 dark:text-brand-300',
  'Low Match': 'bg-rose-100 text-rose-600 dark:bg-rose-500/20 dark:text-rose-100',
}

export default function RecommendationBadge({ recommendation, className }) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded px-2 py-0.5 text-xs font-medium',
        STYLES[recommendation] || 'bg-black/5 text-ink/60',
        className
      )}
    >
      {recommendation}
    </span>
  )
}
