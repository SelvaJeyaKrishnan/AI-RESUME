export default function PageHeader({ eyebrow, title, description, actions }) {
  return (
    <div className="border-b border-line dark:border-lineDark px-5 sm:px-8 py-5 sm:py-6 flex items-start justify-between gap-5 flex-wrap">
      <div>
        {eyebrow && <p className="label-eyebrow mb-1">{eyebrow}</p>}
        <h1 className="font-display text-2xl sm:text-3xl tracking-tight">{title}</h1>
        {description && <p className="text-sm text-ink/60 dark:text-paper/60 mt-1 max-w-xl">{description}</p>}
      </div>
      {actions && <div className="flex items-center gap-2 w-full sm:w-auto">{actions}</div>}
    </div>
  )
}
