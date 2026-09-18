import { Loader2 } from 'lucide-react'

export function Spinner({ className = 'h-5 w-5' }) {
  return <Loader2 className={`animate-spin ${className}`} />
}

export function PageLoader({ label = 'Loading…' }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-ink/50 dark:text-paper/50">
      <Spinner className="h-6 w-6 mb-3" />
      <p className="text-sm">{label}</p>
    </div>
  )
}

export function SkeletonRow() {
  return (
    <div className="flex items-center gap-4 rounded-md border border-line dark:border-lineDark p-4 animate-pulse">
      <div className="h-10 w-10 rounded-full bg-black/10 dark:bg-white/10" />
      <div className="flex-1 space-y-2">
        <div className="h-3 w-1/3 rounded bg-black/10 dark:bg-white/10" />
        <div className="h-3 w-1/2 rounded bg-black/10 dark:bg-white/10" />
      </div>
    </div>
  )
}
