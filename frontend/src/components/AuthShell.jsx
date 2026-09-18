import { ScanSearch, Sparkles } from 'lucide-react'

export default function AuthShell({ title, subtitle, children }) {
  return (
    <div className="min-h-screen flex bg-paper dark:bg-ink text-ink dark:text-paper">
      <div className="hidden lg:flex w-1/2 bg-brand-900 text-paper flex-col justify-between p-12 relative overflow-hidden">
        <div className="flex items-center gap-2">
          <ScanSearch className="h-6 w-6 text-amber-400" strokeWidth={2} />
          <span className="font-display text-xl">ResumeAI</span>
        </div>

        <div className="max-w-md">
          <p className="label-eyebrow text-brand-300 mb-3">Decision-support for recruiters</p>
          <h1 className="font-display text-4xl leading-tight mb-4">
            Screen every resume against the role that matters, in seconds.
          </h1>
          <p className="text-brand-100/80 leading-relaxed">
            Upload a stack of resumes and a job description — ResumeAI ranks candidates,
            explains every score, and leaves the final call to you.
          </p>
        </div>

        <div className="flex items-center gap-2 text-sm text-brand-100/60">
          <Sparkles className="h-4 w-4" />
          Explainable AI matching. No black-box scores.
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <ScanSearch className="h-5 w-5 text-brand-600" strokeWidth={2} />
            <span className="font-display text-lg">ResumeAI</span>
          </div>
          <h2 className="font-display text-2xl mb-1">{title}</h2>
          <p className="text-sm text-ink/60 dark:text-paper/60 mb-6">{subtitle}</p>
          {children}
        </div>
      </div>
    </div>
  )
}
