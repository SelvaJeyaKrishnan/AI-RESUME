import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Plus, Briefcase, Trash2, Users } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import Modal from '../components/Modal.jsx'
import JobForm from '../components/JobForm.jsx'
import EmptyState from '../components/EmptyState.jsx'
import { PageLoader } from '../components/Loaders.jsx'
import { listJobs, deleteJob } from '../services/api.js'

export default function JobsPage() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)

  const load = async () => {
    const { data } = await listJobs()
    setJobs(data)
  }

  useEffect(() => {
    load()
  }, [])

  const onSaved = (job) => {
    setModalOpen(false)
    navigate(`/recruiter/jobs/${job.id}`)
  }

  const onDelete = async (e, jobId) => {
    e.preventDefault()
    e.stopPropagation()
    if (!confirm('Delete this job and all of its analyses? This cannot be undone.')) return
    try {
      await deleteJob(jobId)
      toast.success('Job deleted')
      load()
    } catch {
      toast.error('Could not delete job')
    }
  }

  if (!jobs) return <PageLoader />

  return (
    <div>
      <PageHeader
        eyebrow="Roles"
        title="Jobs"
        description="Each job holds its own requirements and candidate ranking."
        actions={
          <button className="btn-primary" onClick={() => setModalOpen(true)}>
            <Plus className="h-4 w-4" /> New job
          </button>
        }
      />

      <div className="p-8">
        {jobs.length === 0 ? (
          <EmptyState
            icon={Briefcase}
            title="No jobs yet"
            description="Create your first job to start screening resumes against it."
            action={<button className="btn-primary" onClick={() => setModalOpen(true)}><Plus className="h-4 w-4" /> Create a job</button>}
          />
        ) : (
          <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {jobs.map((job) => (
              <Link key={job.id} to={`/recruiter/jobs/${job.id}`} className="card p-5 flex flex-col hover:border-brand-300 transition-colors group">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-display text-lg leading-snug">{job.title}</h3>
                  <button
                    onClick={(e) => onDelete(e, job.id)}
                    className="text-ink/30 hover:text-rose-600 shrink-0"
                    title="Delete job"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {job.required_skills.slice(0, 4).map((s) => (
                    <span key={s} className="text-xs bg-black/5 dark:bg-white/10 rounded px-2 py-0.5">{s}</span>
                  ))}
                  {job.required_skills.length > 4 && (
                    <span className="text-xs text-ink/40 dark:text-paper/40">+{job.required_skills.length - 4} more</span>
                  )}
                </div>
                <div className="mt-auto pt-4 flex items-center justify-between text-sm text-ink/60 dark:text-paper/60">
                  <span className="flex items-center gap-1.5"><Users className="h-3.5 w-3.5" /> {job.candidate_count}</span>
                  <span>{job.avg_score != null ? `${job.avg_score}% avg match` : 'Not analyzed yet'}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Create a job" wide>
        <JobForm onSaved={onSaved} onCancel={() => setModalOpen(false)} />
      </Modal>
    </div>
  )
}
