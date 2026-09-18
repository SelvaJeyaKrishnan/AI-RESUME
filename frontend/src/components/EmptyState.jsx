export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-md border border-dashed border-line dark:border-lineDark py-16 px-6 text-center">
      {Icon && <Icon className="mb-3 h-8 w-8 text-ink/30 dark:text-paper/30" strokeWidth={1.5} />}
      <h3 className="font-display text-lg text-ink dark:text-paper">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm text-ink/60 dark:text-paper/60">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
