import { useEffect, useMemo, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import { Plus, Pencil, Trash2, Search, Users, GitCompare, ArrowUpDown } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import Modal from '../components/Modal.jsx'
import JobForm from '../components/JobForm.jsx'
import EmptyState from '../components/EmptyState.jsx'
import { PageLoader } from '../components/Loaders.jsx'
import ScoreRing from '../components/ScoreRing.jsx'
import RecommendationBadge from '../components/RecommendationBadge.jsx'
import AnalyzeResumesModal from '../components/AnalyzeResumesModal.jsx'
import ComparisonTable from '../components/ComparisonTable.jsx'
import AnalyticsPanel from '../components/AnalyticsPanel.jsx'
import {
  getJob, getJobRanking, getJobAnalytics, deleteJob,
} from '../services/api.js'

const TABS = ['Requirements', 'Candidates', 'Analytics']
const RECOMMENDATIONS = ['Strong Match', 'Good Match', 'Potential Match', 'Low Match']

export default function JobDetailPage() {
  const { jobId } = useParams()
  const navigate = useNavigate()

  const [job, setJob] = useState(null)
  const [ranking, setRanking] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [tab, setTab] = useState('Candidates')

  const [editOpen, setEditOpen] = useState(false)
  const [analyzeOpen, setAnalyzeOpen] = useState(false)

  const [search, setSearch] = useState('')
  const [minScore, setMinScore] = useState(0)
  const [recFilter, setRecFilter] = useState('All')
  const [sortBy, setSortBy] = useState('score_desc')
  const [selected, setSelected] = useState(new Set())

  const load = async () => {
    const [jobRes, rankingRes, analyticsRes] = await Promise.all([
      getJob(jobId), getJobRanking(jobId), getJobAnalytics(jobId),
    ])
    setJob(jobRes.data)
    setRanking(rankingRes.data)
    setAnalytics(analyticsRes.data)
  }

  useEffect(() => {
    load()
    setSelected(new Set())
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId])

  const filteredRanking = useMemo(() => {
    if (!ranking) return []
    let rows = ranking.filter((r) => {
      const name = (r.candidate?.full_name || r.original_filename).toLowerCase()
      if (search && !name.includes(search.toLowerCase())) return false
      if (r.analysis.overall_score < minScore) return false
      if (recFilter !== 'All' && r.analysis.recommendation !== recFilter) return false
      return true
    })
    const sorters = {
      score_desc: (a, b) => b.analysis.overall_score - a.analysis.overall_score,
      score_asc: (a, b) => a.analysis.overall_score - b.analysis.overall_score,
      experience_desc: (a, b) => (b.candidate?.years_of_experience || 0) - (a.candidate?.years_of_experience || 0),
      recent: (a, b) => new Date(b.analysis.analyzed_at) - new Date(a.analysis.analyzed_at),
    }
    return rows.sort(sorters[sortBy])
  }, [ranking, search, minScore, recFilter, sortBy])

  const toggleSelect = (resumeId) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(resumeId)) {
        next.delete(resumeId)
      } else {
        if (next.size >= 3) {
          toast.error('You can compare up to 3 candidates at a time')
          return prev
        }
        next.add(resumeId)
      }
      return next
    })
  }

  const onDeleteJob = async () => {
    if (!confirm('Delete this job and all of its candidate analyses?')) return
    await deleteJob(jobId)
    toast.success('Job deleted')
    navigate('/recruiter/jobs')
  }

  if (!job || !ranking || !analytics) return <PageLoader label="Loading job…" />

  const selectedRows = ranking.filter((r) => selected.has(r.resume_id))

  return (
    <div>
      <PageHeader
        eyebrow="Job"
        title={job.title}
        description={`${job.required_skills.length} required skill${job.required_skills.length === 1 ? '' : 's'} · ${job.required_experience_years || 0}+ yrs experience${job.education_requirement ? ` · ${job.education_requirement}` : ''}`}
        actions={
          <>
            <button className="btn-secondary" onClick={() => setEditOpen(true)}>
              <Pencil className="h-4 w-4" /> Edit
            </button>
            <button className="btn-secondary hover:!text-rose-600" onClick={onDeleteJob}>
              <Trash2 className="h-4 w-4" /> Delete
            </button>
            <button className="btn-primary" onClick={() => setAnalyzeOpen(true)}>
              <Plus className="h-4 w-4" /> Analyze resumes
            </button>
          </>
        }
      />

      <div className="px-8 pt-4 flex gap-1 border-b border-line dark:border-lineDark">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              'px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
              tab === t ? 'border-brand-600 text-brand-600 dark:text-brand-300' : 'border-transparent text-ink/50 hover:text-ink dark:text-paper/50 dark:hover:text-paper'
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="p-8">
        {tab === 'Requirements' && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 card p-6">
              <p className="label-eyebrow mb-3">Full job description</p>
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-ink/80 dark:text-paper/80 font-sans">{job.description_raw}</pre>
            </div>
            <div className="space-y-4">
              <div className="card p-5">
                <p className="label-eyebrow mb-2">Required skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {job.required_skills.map((s) => <span key={s} className="text-xs bg-brand-50 text-brand-700 dark:bg-brand-500/20 dark:text-brand-200 rounded px-2 py-0.5">{s}</span>)}
                </div>
              </div>
              <div className="card p-5">
                <p className="label-eyebrow mb-2">Preferred skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {job.preferred_skills.length
                    ? job.preferred_skills.map((s) => <span key={s} className="text-xs bg-black/5 dark:bg-white/10 rounded px-2 py-0.5">{s}</span>)
                    : <span className="text-xs text-ink/40 dark:text-paper/40">None detected</span>}
                </div>
              </div>
              <div className="card p-5">
                <p className="label-eyebrow mb-2">Responsibilities</p>
                {job.responsibilities.length ? (
                  <ul className="text-sm space-y-1 list-disc list-inside text-ink/70 dark:text-paper/70">
                    {job.responsibilities.slice(0, 6).map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                ) : <p className="text-xs text-ink/40 dark:text-paper/40">None detected</p>}
              </div>
            </div>
          </div>
        )}

        {tab === 'Candidates' && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink/30" />
                <input className="input pl-9" placeholder="Search candidates…" value={search} onChange={(e) => setSearch(e.target.value)} />
              </div>
              <select className="input w-auto" value={recFilter} onChange={(e) => setRecFilter(e.target.value)}>
                <option value="All">All recommendations</option>
                {RECOMMENDATIONS.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
              <select className="input w-auto" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="score_desc">Highest score</option>
                <option value="score_asc">Lowest score</option>
                <option value="experience_desc">Most experience</option>
                <option value="recent">Recently analyzed</option>
              </select>
              <div className="flex items-center gap-2 text-sm text-ink/60 dark:text-paper/60">
                <span>Min score</span>
                <input type="range" min="0" max="100" value={minScore} onChange={(e) => setMinScore(Number(e.target.value))} />
                <span className="font-mono w-8">{minScore}</span>
              </div>
            </div>

            {selected.size >= 2 && (
              <div className="card p-4 flex items-center justify-between bg-brand-50 dark:bg-brand-500/10 border-brand-300">
                <span className="text-sm font-medium flex items-center gap-2">
                  <GitCompare className="h-4 w-4" /> {selected.size} candidates selected for comparison
                </span>
                <div className="flex gap-2">
                  <button className="btn-ghost" onClick={() => setSelected(new Set())}>Clear</button>
                  <button className="btn-primary" onClick={() => setTab('Compare')}>Compare now</button>
                </div>
              </div>
            )}

            {ranking.length === 0 ? (
              <EmptyState
                icon={Users}
                title="No candidates analyzed yet"
                description="Analyze resumes from your library against this job to see ranked results here."
                action={<button className="btn-primary" onClick={() => setAnalyzeOpen(true)}><Plus className="h-4 w-4" /> Analyze resumes</button>}
              />
            ) : filteredRanking.length === 0 ? (
              <EmptyState title="No candidates match your filters" description="Try widening your search or lowering the minimum score." />
            ) : (
              <div className="card divide-y divide-line dark:divide-lineDark">
                {filteredRanking.map((r, idx) => (
                  <div key={r.resume_id} className="flex items-center gap-4 p-4">
                    <input
                      type="checkbox"
                      className="accent-brand-600"
                      checked={selected.has(r.resume_id)}
                      onChange={() => toggleSelect(r.resume_id)}
                    />
                    <span className="font-mono text-sm text-ink/30 dark:text-paper/30 w-6">#{idx + 1}</span>
                    <ScoreRing score={r.analysis.overall_score} size={44} strokeWidth={4} />
                    <div className="min-w-0 flex-1">
                      <Link to={`/recruiter/jobs/${jobId}/candidates/${r.resume_id}`} className="font-medium hover:text-brand-600 dark:hover:text-brand-300 truncate block">
                        {r.candidate?.full_name || r.original_filename}
                      </Link>
                      <p className="text-xs text-ink/50 dark:text-paper/50 truncate">
                        {r.candidate?.years_of_experience || 0} yrs · {r.analysis.matching_skills.slice(0, 3).join(', ') || 'No matching skills'}
                      </p>
                    </div>
                    <RecommendationBadge recommendation={r.analysis.recommendation} className="shrink-0" />
                    <Link to={`/recruiter/jobs/${jobId}/candidates/${r.resume_id}`} className="btn-ghost shrink-0">View</Link>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === 'Compare' && (
          <div className="space-y-4">
            <button className="btn-secondary" onClick={() => setTab('Candidates')}>
              <ArrowUpDown className="h-4 w-4" /> Back to candidates
            </button>
            {selectedRows.length >= 2 ? (
              <div className="card p-6">
                <ComparisonTable candidates={selectedRows} />
              </div>
            ) : (
              <EmptyState title="Select 2–3 candidates" description="Go back to the Candidates tab and check the boxes next to candidates you'd like to compare." />
            )}
          </div>
        )}

        {tab === 'Analytics' && <AnalyticsPanel analytics={analytics} />}
      </div>

      <Modal open={editOpen} onClose={() => setEditOpen(false)} title="Edit job" wide>
        <JobForm job={job} onSaved={() => { setEditOpen(false); load(); }} onCancel={() => setEditOpen(false)} />
      </Modal>

      <Modal open={analyzeOpen} onClose={() => setAnalyzeOpen(false)} title="Analyze resumes against this job" wide>
        <AnalyzeResumesModal
          jobId={jobId}
          alreadyAnalyzedIds={new Set(ranking.map((r) => r.resume_id))}
          onDone={() => { setAnalyzeOpen(false); load(); }}
        />
      </Modal>
    </div>
  )
}
