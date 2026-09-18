import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Mail, Phone, MapPin, Download, CheckCircle2, XCircle, Info } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import ScoreRing from '../components/ScoreRing.jsx'
import RecommendationBadge from '../components/RecommendationBadge.jsx'
import ScoreBreakdown from '../components/ScoreBreakdown.jsx'
import { PageLoader } from '../components/Loaders.jsx'
import { getResume, getJob, getAnalysis, downloadResumeUrl } from '../services/api.js'

export default function CandidateDetailPage() {
  const { jobId, resumeId } = useParams()
  const [resume, setResume] = useState(null)
  const [job, setJob] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getResume(resumeId), getJob(jobId), getAnalysis(resumeId, jobId)])
      .then(([r, j, a]) => {
        setResume(r.data)
        setJob(j.data)
        setAnalysis(a.data)
      })
      .catch((err) => setError(err.response?.data?.detail || 'Could not load this candidate'))
  }, [resumeId, jobId])

  if (error) {
    return (
      <div className="p-8">
        <p className="text-rose-600">{error}</p>
        <Link to={`/recruiter/jobs/${jobId}`} className="text-brand-600 hover:underline text-sm mt-2 inline-block">
          Back to job
        </Link>
      </div>
    )
  }

  if (!resume || !job || !analysis) return <PageLoader label="Loading candidate profile…" />

  const candidate = resume.candidate

  return (
    <div>
      <PageHeader
        eyebrow={job.title}
        title={candidate?.full_name || resume.original_filename}
        actions={
          <Link to={`/recruiter/jobs/${jobId}`} className="btn-secondary">
            <ArrowLeft className="h-4 w-4" /> Back to ranking
          </Link>
        }
      />

      <div className="p-8 grid lg:grid-cols-3 gap-6">
        {/* Left: profile + resume preview */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card p-6">
            <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-ink/70 dark:text-paper/70">
              {candidate?.email && <span className="flex items-center gap-1.5"><Mail className="h-4 w-4" />{candidate.email}</span>}
              {candidate?.phone && <span className="flex items-center gap-1.5"><Phone className="h-4 w-4" />{candidate.phone}</span>}
              {candidate?.location && <span className="flex items-center gap-1.5"><MapPin className="h-4 w-4" />{candidate.location}</span>}
              <a href={downloadResumeUrl(resume.id)} className="flex items-center gap-1.5 text-brand-600 dark:text-brand-300 hover:underline ml-auto">
                <Download className="h-4 w-4" /> Download resume
              </a>
            </div>

            <div className="mt-5 grid sm:grid-cols-2 gap-6">
              <div>
                <p className="label-eyebrow mb-2">Experience</p>
                <p className="text-2xl font-display">{candidate?.years_of_experience || 0} yrs</p>
                <ul className="mt-2 space-y-1 text-sm text-ink/70 dark:text-paper/70">
                  {(candidate?.work_experience || []).slice(0, 3).map((e, i) => (
                    <li key={i} className="truncate">{e.context}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="label-eyebrow mb-2">Education</p>
                <ul className="space-y-1 text-sm text-ink/70 dark:text-paper/70">
                  {(candidate?.education || []).length
                    ? candidate.education.slice(0, 3).map((e, i) => <li key={i}>{e.degree_line}</li>)
                    : <li className="text-ink/40 dark:text-paper/40">Not detected</li>}
                </ul>
              </div>
            </div>

            {candidate?.certifications?.length > 0 && (
              <div className="mt-5">
                <p className="label-eyebrow mb-2">Certifications</p>
                <div className="flex flex-wrap gap-1.5">
                  {candidate.certifications.map((c, i) => (
                    <span key={i} className="text-xs bg-black/5 dark:bg-white/10 rounded px-2 py-0.5">{c}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-5">
              <p className="label-eyebrow mb-2">All detected skills</p>
              <div className="flex flex-wrap gap-1.5">
                {(candidate?.skills || []).map((s) => (
                  <span key={s} className="text-xs bg-brand-50 text-brand-700 dark:bg-brand-500/20 dark:text-brand-200 rounded px-2 py-0.5">{s}</span>
                ))}
              </div>
            </div>
          </div>

          <div className="card p-6">
            <p className="label-eyebrow mb-3">Resume preview</p>
            <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-ink/70 dark:text-paper/70 max-h-96 overflow-y-auto">
              {resume.raw_text_preview || 'Preview not available.'}
            </pre>
          </div>
        </div>

        {/* Right: AI match analysis */}
        <div className="space-y-6">
          <div className="card p-6 text-center">
            <div className="flex justify-center mb-3">
              <ScoreRing score={analysis.overall_score} size={88} strokeWidth={7} />
            </div>
            <RecommendationBadge recommendation={analysis.recommendation} className="text-sm px-3 py-1" />
            <p className="text-xs text-ink/40 dark:text-paper/40 mt-3 flex items-center justify-center gap-1">
              <Info className="h-3 w-3" /> AI-generated — verify before deciding
            </p>
          </div>

          <div className="card p-6">
            <p className="label-eyebrow mb-3">Score breakdown</p>
            <ScoreBreakdown analysis={analysis} />
          </div>

          <div className="card p-6">
            <p className="label-eyebrow mb-3">AI summary</p>
            <p className="text-sm leading-relaxed text-ink/80 dark:text-paper/80">{analysis.ai_summary}</p>
          </div>

          <div className="card p-6">
            <p className="label-eyebrow mb-3">Strengths</p>
            <ul className="space-y-1.5 text-sm">
              {analysis.strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sage-600 dark:text-sage-500">
                  <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5" /> <span className="text-ink/80 dark:text-paper/80">{s}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="card p-6">
            <p className="label-eyebrow mb-3">Potential gaps</p>
            <ul className="space-y-1.5 text-sm">
              {analysis.gaps.length ? analysis.gaps.map((g, i) => (
                <li key={i} className="flex items-start gap-2 text-rose-600">
                  <XCircle className="h-4 w-4 shrink-0 mt-0.5" /> <span className="text-ink/80 dark:text-paper/80">{g}</span>
                </li>
              )) : <li className="text-ink/40 dark:text-paper/40 text-sm">No significant gaps detected</li>}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
