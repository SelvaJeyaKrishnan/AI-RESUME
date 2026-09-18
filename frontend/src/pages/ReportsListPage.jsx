import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { FileText, Lock, Trash2, ArrowRight, Plus } from 'lucide-react'
import { PageLoader } from '../components/Loaders.jsx'
import EmptyState from '../components/EmptyState.jsx'
import { Reveal } from '../components/Motion.jsx'
import { bandColor } from '../components/ScoreGauge.jsx'
import { listCareerReports, deleteCareerReport } from '../services/api.js'

export default function ReportsListPage() {
  const [reports, setReports] = useState(null)
  const navigate = useNavigate()

  const load = async () => {
    try {
      const { data } = await listCareerReports()
      setReports(data)
    } catch {
      toast.error('Could not load your reports.')
      setReports([])
    }
  }

  useEffect(() => { load() }, [])

  const onDelete = async (e, id) => {
    e.preventDefault()
    e.stopPropagation()
    if (!confirm('Delete this report? This cannot be undone.')) return
    try {
      await deleteCareerReport(id)
      toast.success('Report deleted')
      load()
    } catch {
      toast.error('Could not delete that report.')
    }
  }

  if (!reports) return <PageLoader label="Loading your reports…" />

  return (
    <div className="container-page py-10 sm:py-14 max-w-4xl">
      <Reveal>
        <div className="flex items-start justify-between gap-4 flex-wrap mb-8">
          <div>
            <h1 className="font-display text-3xl tracking-tight">My Reports</h1>
            <p className="mt-1 text-ink/65 dark:text-paper/65">Every resume analysis you've run.</p>
          </div>
          <Link to="/analyze" className="btn-primary"><Plus className="h-4 w-4" /> New analysis</Link>
        </div>
      </Reveal>

      {reports.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No reports yet"
          description="Upload a resume and describe your target role to generate your first career report."
          action={<Link to="/analyze" className="btn-primary">Analyze my resume</Link>}
        />
      ) : (
        <div className="space-y-3">
          {reports.map((r, i) => {
            const locked = r.status !== 'complete'
            const destination = locked ? `/assessment/${r.id}` : `/report/${r.id}`
            return (
              <Reveal key={r.id} delay={i * 0.05}>
                <Link to={destination} className="card p-5 flex items-center gap-4 hover:border-brand-300 transition-colors group">
                  <div className="h-10 w-10 rounded bg-brand-50 dark:bg-brand-500/20 flex items-center justify-center shrink-0">
                    {locked ? <Lock className="h-4 w-4 text-ink/40" /> : <FileText className="h-4 w-4 text-brand-600 dark:text-brand-300" />}
                  </div>

                  <div className="min-w-0 flex-1">
                    <p className="font-medium truncate">{r.target_job_title || 'Untitled role'}</p>
                    <p className="text-xs text-ink/50 dark:text-paper/50">
                      {new Date(r.created_at).toLocaleDateString()} ·{' '}
                      {locked ? 'Assessment pending' : 'Complete'}
                    </p>
                  </div>

                  {!locked && (
                    <div className="hidden sm:flex items-center gap-5 shrink-0 text-center">
                      {[
                        { label: 'ATS', value: r.ats_score },
                        { label: 'Overall', value: r.overall_score },
                        { label: 'Match', value: r.job_match_score },
                      ].map((s) => (
                        <div key={s.label}>
                          <p className="font-mono text-sm" style={{ color: bandColor(s.value || 0) }}>
                            {Math.round(s.value || 0)}
                          </p>
                          <p className="label-eyebrow">{s.label}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  <button onClick={(e) => onDelete(e, r.id)} className="btn-ghost !px-2 shrink-0 hover:!text-rose-600" title="Delete">
                    <Trash2 className="h-4 w-4" />
                  </button>
                  <ArrowRight className="h-4 w-4 text-ink/25 group-hover:text-brand-600 transition-colors shrink-0" />
                </Link>
              </Reveal>
            )
          })}
        </div>
      )}
    </div>
  )
}
