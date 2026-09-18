import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { CheckCircle2, FileText } from 'lucide-react'
import { listResumes, analyzeResume } from '../services/api.js'
import { Spinner } from './Loaders.jsx'
import UploadDropzone from './UploadDropzone.jsx'

export default function AnalyzeResumesModal({ jobId, alreadyAnalyzedIds, onDone }) {
  const [resumes, setResumes] = useState(null)
  const [selected, setSelected] = useState(new Set())
  const [running, setRunning] = useState(false)

  const load = async () => {
    const { data } = await listResumes()
    setResumes(data.filter((r) => r.parse_status === 'success'))
  }

  useEffect(() => {
    load()
  }, [])

  const toggle = (id) => {
    setSelected((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const runAnalysis = async () => {
    if (selected.size === 0) return
    setRunning(true)
    let success = 0
    for (const resumeId of selected) {
      try {
        await analyzeResume(resumeId, jobId)
        success += 1
      } catch (err) {
        toast.error(`Failed to analyze one resume: ${err.response?.data?.detail || 'unknown error'}`)
      }
    }
    setRunning(false)
    toast.success(`Analyzed ${success} candidate${success === 1 ? '' : 's'} against this job`)
    onDone?.()
  }

  if (!resumes) return <div className="py-8 flex justify-center"><Spinner /></div>

  return (
    <div>
      <div className="mb-4">
        <UploadDropzone onUploaded={load} />
      </div>

      {resumes.length === 0 ? (
        <p className="text-sm text-ink/50 dark:text-paper/50 text-center py-6">
          No parsed resumes in your library yet. Upload some above.
        </p>
      ) : (
        <div className="max-h-72 overflow-y-auto space-y-1 border border-line dark:border-lineDark rounded-md">
          {resumes.map((r) => {
            const already = alreadyAnalyzedIds.has(r.id)
            return (
              <label
                key={r.id}
                className={`flex items-center gap-3 px-3 py-2.5 border-b last:border-b-0 border-line dark:border-lineDark cursor-pointer hover:bg-black/5 dark:hover:bg-white/5 ${already ? 'opacity-50' : ''}`}
              >
                <input
                  type="checkbox"
                  checked={selected.has(r.id)}
                  onChange={() => toggle(r.id)}
                  className="accent-brand-600"
                />
                <FileText className="h-4 w-4 text-ink/30 shrink-0" />
                <span className="text-sm flex-1 truncate">{r.candidate?.full_name || r.original_filename}</span>
                {already && <span className="text-xs text-sage-600 flex items-center gap-1"><CheckCircle2 className="h-3.5 w-3.5" /> Already analyzed</span>}
              </label>
            )
          })}
        </div>
      )}

      <div className="flex justify-end gap-2 mt-4">
        <button className="btn-primary" onClick={runAnalysis} disabled={running || selected.size === 0}>
          {running && <Spinner className="h-4 w-4" />}
          Analyze {selected.size > 0 ? `${selected.size} candidate${selected.size === 1 ? '' : 's'}` : ''}
        </button>
      </div>
    </div>
  )
}
