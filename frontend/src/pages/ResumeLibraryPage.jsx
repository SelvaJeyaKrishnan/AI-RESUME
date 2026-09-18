import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { FileText, Trash2, Download, RefreshCw, AlertTriangle, CheckCircle2 } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import UploadDropzone from '../components/UploadDropzone.jsx'
import EmptyState from '../components/EmptyState.jsx'
import { PageLoader, Spinner } from '../components/Loaders.jsx'
import { listResumes, deleteResume, reprocessResume, downloadResumeUrl } from '../services/api.js'

export default function ResumeLibraryPage() {
  const [resumes, setResumes] = useState(null)
  const [busyId, setBusyId] = useState(null)

  const load = async () => {
    const { data } = await listResumes()
    setResumes(data)
  }

  useEffect(() => {
    load()
  }, [])

  const onDelete = async (id) => {
    if (!confirm('Delete this resume? Any analyses tied to it will also be removed.')) return
    setBusyId(id)
    try {
      await deleteResume(id)
      toast.success('Resume deleted')
      load()
    } catch {
      toast.error('Could not delete resume')
    } finally {
      setBusyId(null)
    }
  }

  const onReprocess = async (id) => {
    setBusyId(id)
    try {
      await reprocessResume(id)
      toast.success('Resume re-analyzed')
      load()
    } catch {
      toast.error('Re-analysis failed')
    } finally {
      setBusyId(null)
    }
  }

  if (!resumes) return <PageLoader />

  return (
    <div>
      <PageHeader
        eyebrow="Library"
        title="Resume library"
        description="Every resume you've uploaded, independent of any specific job. Analyze them from a job's Candidates tab."
      />

      <div className="p-8 space-y-6">
        <UploadDropzone onUploaded={load} />

        {resumes.length === 0 ? (
          <EmptyState icon={FileText} title="No resumes uploaded yet" description="Drag a few resumes above to get started." />
        ) : (
          <div className="card divide-y divide-line dark:divide-lineDark">
            {resumes.map((r) => (
              <div key={r.id} className="flex items-center gap-4 p-4">
                <FileText className="h-5 w-5 text-ink/30 dark:text-paper/30 shrink-0" />
                <div className="min-w-0 flex-1">
                  <p className="font-medium truncate">{r.candidate?.full_name || r.original_filename}</p>
                  <p className="text-xs text-ink/50 dark:text-paper/50 truncate">
                    {r.original_filename} · {r.candidate?.email || 'no email detected'}
                  </p>
                </div>

                {r.parse_status === 'success' ? (
                  <span className="flex items-center gap-1 text-xs text-sage-600 shrink-0">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Parsed
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-xs text-rose-600 shrink-0" title={r.parse_error}>
                    <AlertTriangle className="h-3.5 w-3.5" /> Failed
                  </span>
                )}

                <div className="flex items-center gap-1 shrink-0">
                  <a href={downloadResumeUrl(r.id)} className="btn-ghost !px-2" title="Download">
                    <Download className="h-4 w-4" />
                  </a>
                  <button onClick={() => onReprocess(r.id)} className="btn-ghost !px-2" title="Re-analyze" disabled={busyId === r.id}>
                    {busyId === r.id ? <Spinner className="h-4 w-4" /> : <RefreshCw className="h-4 w-4" />}
                  </button>
                  <button onClick={() => onDelete(r.id)} className="btn-ghost !px-2 hover:!text-rose-600" title="Delete">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
