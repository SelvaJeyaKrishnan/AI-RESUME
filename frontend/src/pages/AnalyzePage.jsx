import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { UploadCloud, FileText, X, AlertCircle, ArrowRight } from 'lucide-react'
import { Spinner } from '../components/Loaders.jsx'
import { Reveal } from '../components/Motion.jsx'
import { createCareerReport } from '../services/api.js'

const ACCEPTED = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
}
const MAX_BYTES = 10 * 1024 * 1024

const PLACEHOLDER =
  'Example: Python Developer with experience in Flask, FastAPI, SQL, REST APIs, Git and basic machine learning.\n\n' +
  'Paste the full job posting here if you have it — the more detail you include, the more accurate your match analysis will be.'

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

export default function AnalyzePage() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [progress, setProgress] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors] = useState({})

  const onDrop = useCallback((accepted, rejected) => {
    if (rejected?.length) {
      const r = rejected[0]
      const tooBig = r.errors?.some((e) => e.code === 'file-too-large')
      setErrors((prev) => ({
        ...prev,
        file: tooBig
          ? `That file is ${formatSize(r.file.size)}. Please upload a resume under 10MB.`
          : `"${r.file.name}" isn't a supported format. Please upload a PDF, DOCX or TXT file.`,
      }))
      return
    }
    if (accepted[0]) {
      setFile(accepted[0])
      setErrors((prev) => ({ ...prev, file: null }))
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: ACCEPTED, maxSize: MAX_BYTES, multiple: false,
  })

  const validate = () => {
    const next = {}
    if (!file) next.file = 'Please upload your resume before analyzing.'
    if (!jobDescription.trim()) {
      next.jobDescription = 'Please describe the role you are targeting so we can compare your resume against it.'
    } else if (jobDescription.trim().length < 20) {
      next.jobDescription = 'Please add a little more detail — at least a sentence about the role and its key skills.'
    }
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    if (submitting) return          // guard against duplicate submissions
    if (!validate()) return

    setSubmitting(true)
    setProgress(0)
    try {
      const { data } = await createCareerReport(
        file, jobDescription, jobTitle || undefined,
        (evt) => {
          if (evt.total) setProgress(Math.round((evt.loaded / evt.total) * 100))
        }
      )
      toast.success('Resume processed. One quick challenge before your report.')
      navigate(`/assessment/${data.report_id}`, { state: { meta: data } })
    } catch (err) {
      const status = err.response?.status
      const detail = err.response?.data?.detail
      if (status === 415 || status === 413 || status === 422) {
        setErrors({ file: typeof detail === 'string' ? detail : 'We could not read that resume file.' })
      } else if (status === 400) {
        setErrors({ jobDescription: typeof detail === 'string' ? detail : 'Please check the job description.' })
      } else if (!err.response) {
        toast.error('Cannot reach the server. Check that the backend is running and try again.')
      } else {
        toast.error(typeof detail === 'string' ? detail : 'Something went wrong analyzing your resume.')
      }
      setSubmitting(false)
      setProgress(0)
    }
  }

  return (
    <div className="container-page py-10 sm:py-14 max-w-4xl">
      <Reveal>
        <h1 className="font-display text-3xl sm:text-4xl tracking-tight">Let's Analyze Your Resume</h1>
        <p className="mt-2 text-ink/65 dark:text-paper/65">
          Upload your resume and tell us what role you're targeting.
        </p>
      </Reveal>

      <form onSubmit={onSubmit} className="mt-8 space-y-6" noValidate>
        {/* Upload */}
        <Reveal delay={0.05}>
          <div className="card p-6">
            <label className="label-eyebrow mb-3 block">Step 1 — Your resume</label>

            <AnimatePresence mode="wait">
              {!file ? (
                <motion.div
                  key="dropzone"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  {...getRootProps()}
                  className={`rounded-md border-2 border-dashed px-6 py-12 text-center cursor-pointer transition-colors ${
                    isDragActive
                      ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/10'
                      : errors.file
                        ? 'border-rose-500/60'
                        : 'border-line dark:border-lineDark hover:border-brand-300'
                  }`}
                >
                  <input {...getInputProps()} />
                  <UploadCloud className="mx-auto h-8 w-8 text-ink/35 dark:text-paper/35 mb-3" strokeWidth={1.5} />
                  <p className="font-medium">
                    {isDragActive ? 'Drop your resume here' : 'Drag and drop your resume, or click to browse'}
                  </p>
                  <p className="text-xs text-ink/45 dark:text-paper/45 mt-1">PDF, DOCX or TXT — up to 10MB</p>
                </motion.div>
              ) : (
                <motion.div
                  key="file"
                  initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  className="flex items-center gap-4 rounded-md border border-line dark:border-lineDark p-4"
                >
                  <div className="h-10 w-10 rounded bg-brand-50 dark:bg-brand-500/20 flex items-center justify-center shrink-0">
                    <FileText className="h-5 w-5 text-brand-600 dark:text-brand-300" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium truncate">{file.name}</p>
                    <p className="text-xs text-ink/50 dark:text-paper/50">
                      {(file.name.split('.').pop() || '').toUpperCase()} · {formatSize(file.size)}
                    </p>
                    {submitting && (
                      <div className="mt-2 h-1 rounded-full bg-black/10 dark:bg-white/10 overflow-hidden">
                        <motion.div
                          className="h-full bg-brand-500"
                          initial={{ width: 0 }}
                          animate={{ width: `${progress}%` }}
                          transition={{ duration: 0.2 }}
                        />
                      </div>
                    )}
                  </div>
                  {!submitting && (
                    <button
                      type="button"
                      onClick={() => { setFile(null); setProgress(0) }}
                      className="btn-ghost !px-2 shrink-0"
                      title="Remove file"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {errors.file && (
              <p className="mt-3 flex items-start gap-2 text-sm text-rose-600">
                <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" /> {errors.file}
              </p>
            )}
          </div>
        </Reveal>

        {/* Job description */}
        <Reveal delay={0.1}>
          <div className="card p-6">
            <label className="label-eyebrow mb-3 block">Step 2 — Target job description</label>

            <input
              className="input mb-3"
              placeholder="Job title (optional) — e.g. Python Developer"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              disabled={submitting}
            />

            <textarea
              className={`input min-h-[180px] leading-relaxed ${errors.jobDescription ? '!border-rose-500/60' : ''}`}
              placeholder={PLACEHOLDER}
              value={jobDescription}
              onChange={(e) => {
                setJobDescription(e.target.value)
                if (errors.jobDescription) setErrors((p) => ({ ...p, jobDescription: null }))
              }}
              disabled={submitting}
            />

            <div className="mt-2 flex items-center justify-between text-xs">
              <span className="text-ink/45 dark:text-paper/45">
                The more of the real posting you paste, the more accurate your match.
              </span>
              <span className="font-mono text-ink/40 dark:text-paper/40">
                {jobDescription.trim().length} chars
              </span>
            </div>

            {errors.jobDescription && (
              <p className="mt-3 flex items-start gap-2 text-sm text-rose-600">
                <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" /> {errors.jobDescription}
              </p>
            )}
          </div>
        </Reveal>

        <Reveal delay={0.15}>
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            <button type="submit" className="btn-primary btn-lg" disabled={submitting}>
              {submitting ? <><Spinner className="h-4 w-4" /> Processing your resume…</> : <>Analyze My Resume <ArrowRight className="h-4 w-4" /></>}
            </button>
            <p className="text-xs text-ink/50 dark:text-paper/50 max-w-sm">
              Next you'll complete a short communication challenge — it's part of your career
              assessment, and your report unlocks right after.
            </p>
          </div>
        </Reveal>
      </form>
    </div>
  )
}
