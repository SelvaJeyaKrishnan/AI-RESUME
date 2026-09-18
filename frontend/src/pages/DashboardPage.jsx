import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Briefcase, ArrowRight, Plus } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import StatCard from '../components/StatCard.jsx'
import UploadDropzone from '../components/UploadDropzone.jsx'
import EmptyState from '../components/EmptyState.jsx'
import { PageLoader } from '../components/Loaders.jsx'
import RecommendationBadge from '../components/RecommendationBadge.jsx'
import { listJobs, listResumes, getJobAnalytics } from '../services/api.js'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState(null)
  const [resumes, setResumes] = useState(null)
  const [aggregate, setAggregate] = useState({ total: 0, shortlisted: 0, avg: 0 })

  const load = async () => {
    const [jobsRes, resumesRes] = await Promise.all([listJobs(), listResumes()])
    setJobs(jobsRes.data)
    setResumes(resumesRes.data)

    if (jobsRes.data.length) {
      const analytics = await Promise.all(jobsRes.data.map((j) => getJobAnalytics(j.id).then((r) => r.data)))
      const total = analytics.reduce((s, a) => s + a.total_candidates, 0)
      const shortlisted = analytics.reduce((s, a) => s + a.shortlisted_candidates, 0)
      const weightedAvg =
        analytics.reduce((s, a) => s + a.average_match_score * a.total_candidates, 0) / (total || 1)
      setAggregate({ total, shortlisted, avg: total ? weightedAvg.toFixed(1) : 0 })
    }
  }

  useEffect(() => {
    load()
  }, [])

  if (!jobs || !resumes) return <PageLoader label="Loading your dashboard…" />

  const processed = resumes.filter((r) => r.parse_status === 'success').length
  const failed = resumes.filter((r) => r.parse_status === 'failed').length
  const pending = resumes.length - processed - failed

  return (
    <div>
      <PageHeader
        eyebrow="Overview"
        title="Recruiter dashboard"
        description="Track candidate pipelines across every open role."
        actions={
          <button className="btn-primary" onClick={() => navigate('/recruiter/jobs')}>
            <Plus className="h-4 w-4" /> New job
          </button>
        }
      />

      <div className="p-8 space-y-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total candidates" value={aggregate.total} hint="Analyzed across all jobs" />
          <StatCard label="Processed resumes" value={processed} hint={`${resumes.length} uploaded total`} />
          <StatCard label="Shortlisted" value={aggregate.shortlisted} tone="sage" hint="Strong + Good matches" />
          <StatCard label="Avg. match score" value={aggregate.total ? `${aggregate.avg}%` : '—'} tone="amber" />
        </div>

        {(pending > 0 || failed > 0) && (
          <div className="card p-4 flex items-center gap-6 text-sm">
            <span className="label-eyebrow">Processing status</span>
            {pending > 0 && <span className="text-ink/70 dark:text-paper/70">{pending} pending</span>}
            {failed > 0 && <span className="text-rose-600">{failed} failed to parse</span>}
            {processed > 0 && <span className="text-sage-600">{processed} ready</span>}
          </div>
        )}

        <div className="grid lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3">
            <h2 className="font-display text-lg mb-3">Recent jobs</h2>
            {jobs.length === 0 ? (
              <EmptyState
                icon={Briefcase}
                title="No jobs yet"
                description="Create a job and paste in a description to start screening candidates."
                action={
                  <button className="btn-primary" onClick={() => navigate('/recruiter/jobs')}>
                    <Plus className="h-4 w-4" /> Create your first job
                  </button>
                }
              />
            ) : (
              <div className="space-y-3">
                {jobs.slice(0, 5).map((job) => (
                  <Link
                    key={job.id}
                    to={`/recruiter/jobs/${job.id}`}
                    className="card flex items-center justify-between p-4 hover:border-brand-300 transition-colors group"
                  >
                    <div className="min-w-0">
                      <p className="font-medium truncate">{job.title}</p>
                      <p className="text-xs text-ink/50 dark:text-paper/50 mt-0.5">
                        {job.candidate_count} candidate{job.candidate_count === 1 ? '' : 's'} ·{' '}
                        {job.avg_score != null ? `${job.avg_score}% avg` : 'not yet analyzed'}
                      </p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-ink/30 group-hover:text-brand-600 transition-colors shrink-0 ml-4" />
                  </Link>
                ))}
              </div>
            )}
          </div>

          <div className="lg:col-span-2">
            <h2 className="font-display text-lg mb-3">Upload resumes</h2>
            <UploadDropzone onUploaded={load} />
            <p className="text-xs text-ink/40 dark:text-paper/40 mt-2">
              Uploaded resumes land in your resume library — analyze them against any job from there.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
