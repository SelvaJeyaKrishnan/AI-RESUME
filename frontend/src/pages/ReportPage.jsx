import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles, User, Mail, Phone, MapPin, CheckCircle2, AlertTriangle, Target,
  Lightbulb, Compass, MessageSquareText, FileText, ArrowRight, Info, Lock,
} from 'lucide-react'
import { PageLoader } from '../components/Loaders.jsx'
import { Reveal, CountUp } from '../components/Motion.jsx'
import ScoreGauge, { bandColor } from '../components/ScoreGauge.jsx'
import { getCareerReport } from '../services/api.js'

const PRIORITY_STYLES = {
  high: 'bg-rose-100 text-rose-600 dark:bg-rose-500/20 dark:text-rose-100',
  medium: 'bg-amber-400/20 text-amber-600 dark:text-amber-400',
  low: 'bg-black/5 text-ink/60 dark:bg-white/10 dark:text-paper/60',
}

function SectionHeading({ icon: Icon, title, description }) {
  return (
    <div className="mb-5">
      <div className="flex items-center gap-2 mb-1.5">
        <Icon className="h-4 w-4 text-brand-600 dark:text-brand-300" />
        <h2 className="font-display text-xl tracking-tight">{title}</h2>
      </div>
      {description && <p className="text-sm text-ink/60 dark:text-paper/60">{description}</p>}
    </div>
  )
}

function ScoreBar({ score }) {
  return (
    <div className="h-1.5 rounded-full bg-black/8 dark:bg-white/10 overflow-hidden">
      <motion.div
        className="h-full rounded-full"
        style={{ background: bandColor(score) }}
        initial={{ width: 0 }}
        whileInView={{ width: `${Math.min(Math.max(score, 0), 100)}%` }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      />
    </div>
  )
}

export default function ReportPage() {
  const { reportId } = useParams()
  const navigate = useNavigate()
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)
  const [revealed, setRevealed] = useState(false)

  useEffect(() => {
    getCareerReport(reportId)
      .then(({ data }) => {
        setReport(data)
        // Short reveal beat, then show the report
        setTimeout(() => setRevealed(true), 1100)
      })
      .catch((err) => {
        if (err.response?.status === 403) {
          setError({ locked: true, message: 'Complete the communication assessment to unlock this report.' })
        } else if (err.response?.status === 404) {
          setError({ message: "We couldn't find that report." })
        } else if (!err.response) {
          setError({ message: 'Cannot reach the server. Check that the backend is running.' })
        } else {
          setError({ message: err.response?.data?.detail || 'Could not load your report.' })
        }
      })
  }, [reportId])

  if (error) {
    return (
      <div className="container-page py-20 max-w-lg text-center">
        {error.locked && <Lock className="mx-auto h-8 w-8 text-ink/30 mb-4" />}
        <p className="text-ink/70 dark:text-paper/70 mb-5">{error.message}</p>
        {error.locked ? (
          <button className="btn-primary" onClick={() => navigate(`/assessment/${reportId}`)}>
            Go to the assessment <ArrowRight className="h-4 w-4" />
          </button>
        ) : (
          <Link to="/analyze" className="btn-primary">Start a new analysis</Link>
        )}
      </div>
    )
  }

  if (!report) return <PageLoader label="Loading your career report…" />

  // Reveal transition
  if (!revealed) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }} className="text-center px-6"
        >
          <motion.div
            animate={{ rotate: [0, 8, -8, 0] }}
            transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
            className="inline-flex mb-5"
          >
            <Sparkles className="h-9 w-9 text-amber-400" />
          </motion.div>
          <h1 className="font-display text-3xl sm:text-4xl mb-2">Your Career Report Is Ready.</h1>
          <p className="text-ink/55 dark:text-paper/55 text-sm">Bringing everything together…</p>
        </motion.div>
      </div>
    )
  }

  const c = report.candidate || {}
  const gap = report.skill_gap || {}
  const comm = report.communication

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="bg-hero-wash border-b border-line dark:border-lineDark">
          <div className="container-page py-10">
            <p className="label-eyebrow mb-2">AI Career Report</p>
            <h1 className="font-display text-3xl sm:text-4xl tracking-tight">
              {c.full_name || 'Your resume'}
            </h1>
            <p className="mt-2 text-ink/65 dark:text-paper/65">
              Measured against: <span className="font-medium">{report.target_job_title || 'your target role'}</span>
            </p>

            {/* Headline scores */}
            <div className="mt-8 grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="card p-6 flex justify-center">
                <ScoreGauge score={report.ats_score} label="ATS Compatibility" size={130} />
              </div>
              <div className="card p-6 flex justify-center">
                <ScoreGauge score={report.overall_score} label="Overall Resume Score" size={130} />
              </div>
              <div className="card p-6 flex justify-center">
                <ScoreGauge score={report.job_match_score} label="Job Match" size={130} />
              </div>
              <div className="card p-6 flex flex-col items-center justify-center text-center">
                <MessageSquareText className="h-6 w-6 text-brand-600 dark:text-brand-300 mb-2" />
                {comm ? (
                  <>
                    <p className="font-display text-3xl">
                      <CountUp value={comm.correct} />/{comm.total}
                    </p>
                    <p className="mt-2 font-medium text-sm">Communication</p>
                    <p className="text-xs text-ink/50 dark:text-paper/50">{comm.accuracy}% · {comm.band}</p>
                  </>
                ) : (
                  <p className="text-sm text-ink/50">Not completed</p>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="container-page py-10 space-y-12">
          {/* Resume overview */}
          <Reveal>
            <section>
              <SectionHeading icon={User} title="Resume Overview" description="What we extracted from your resume." />
              <div className="card p-6">
                <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-ink/70 dark:text-paper/70 mb-5">
                  {c.email && <span className="flex items-center gap-1.5"><Mail className="h-4 w-4" />{c.email}</span>}
                  {c.phone && <span className="flex items-center gap-1.5"><Phone className="h-4 w-4" />{c.phone}</span>}
                  {c.location && <span className="flex items-center gap-1.5"><MapPin className="h-4 w-4" />{c.location}</span>}
                  <span className="flex items-center gap-1.5"><FileText className="h-4 w-4" />{report.resume?.filename}</span>
                </div>

                <div className="grid sm:grid-cols-3 gap-6">
                  <div>
                    <p className="label-eyebrow mb-2">Experience</p>
                    <p className="font-display text-2xl">{c.years_of_experience ?? 0} yrs</p>
                  </div>
                  <div>
                    <p className="label-eyebrow mb-2">Education</p>
                    {(c.education || []).length ? (
                      <ul className="text-sm space-y-1 text-ink/70 dark:text-paper/70">
                        {c.education.slice(0, 2).map((e, i) => <li key={i}>{e.degree_line}</li>)}
                      </ul>
                    ) : <p className="text-sm text-ink/40">Not detected</p>}
                  </div>
                  <div>
                    <p className="label-eyebrow mb-2">Projects</p>
                    <p className="font-display text-2xl">{(c.projects || []).length}</p>
                  </div>
                </div>
              </div>
            </section>
          </Reveal>

          {/* ATS breakdown */}
          <Reveal>
            <section>
              <SectionHeading
                icon={Target} title="ATS Compatibility Breakdown"
                description="How an applicant tracking system is likely to read your resume, factor by factor."
              />
              <div className="grid md:grid-cols-2 gap-4">
                {(report.ats?.factors || []).map((f) => (
                  <div key={f.key} className="card p-5">
                    <div className="flex items-baseline justify-between mb-2">
                      <h3 className="font-medium text-sm">{f.label}</h3>
                      <span className="font-mono text-sm" style={{ color: bandColor(f.score) }}>
                        {Math.round(f.score)}
                      </span>
                    </div>
                    <ScoreBar score={f.score} />
                    <p className="text-xs text-ink/60 dark:text-paper/60 mt-3 leading-relaxed">{f.detail}</p>
                    <p className="text-xs text-brand-600 dark:text-brand-300 mt-2 leading-relaxed">{f.suggestion}</p>
                    <p className="text-[10px] font-mono text-ink/30 dark:text-paper/30 mt-2">
                      weight {Math.round(f.weight * 100)}%
                    </p>
                  </div>
                ))}
              </div>
            </section>
          </Reveal>

          {/* Category ratings */}
          <Reveal>
            <section>
              <SectionHeading
                icon={Sparkles} title="Complete Resume Rating"
                description="Your overall score, broken into the categories that produced it."
              />
              <div className="card divide-y divide-line dark:divide-lineDark">
                {(report.ratings || []).map((r) => (
                  <div key={r.key} className="p-5">
                    <div className="flex items-baseline justify-between mb-2 gap-4">
                      <h3 className="font-medium text-sm">{r.label}</h3>
                      <span className="font-mono text-sm shrink-0" style={{ color: bandColor(r.score) }}>
                        {Math.round(r.score)}/100
                      </span>
                    </div>
                    <ScoreBar score={r.score} />
                    <p className="text-xs text-ink/60 dark:text-paper/60 mt-3">{r.explanation}</p>
                    <p className="text-xs text-brand-600 dark:text-brand-300 mt-1.5">{r.suggestion}</p>
                  </div>
                ))}
              </div>
            </section>
          </Reveal>

          {/* Strengths & weaknesses */}
          <Reveal>
            <section className="grid md:grid-cols-2 gap-4">
              <div className="card p-6">
                <SectionHeading icon={CheckCircle2} title="Strengths" />
                <ul className="space-y-2.5">
                  {(report.strengths || []).map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <CheckCircle2 className="h-4 w-4 text-sage-600 shrink-0 mt-0.5" />
                      <span className="text-ink/75 dark:text-paper/75">{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="card p-6">
                <SectionHeading icon={AlertTriangle} title="Areas to Improve" />
                <ul className="space-y-2.5">
                  {(report.weaknesses || []).length ? report.weaknesses.map((w, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                      <span className="text-ink/75 dark:text-paper/75">{w}</span>
                    </li>
                  )) : <li className="text-sm text-ink/45">No significant weaknesses detected in these categories.</li>}
                </ul>
              </div>
            </section>
          </Reveal>

          {/* Job recommendations */}
          <Reveal>
            <section>
              <SectionHeading
                icon={Compass} title="Recommended Roles"
                description="Ranked by how well the skills detected in your resume align with each role."
              />
              <div className="grid md:grid-cols-2 gap-4">
                {(report.roles || []).map((role) => (
                  <div key={role.role} className="card p-5">
                    <div className="flex items-baseline justify-between mb-1 gap-3">
                      <h3 className="font-display text-lg">{role.role}</h3>
                      <span className="font-mono text-lg shrink-0" style={{ color: bandColor(role.match_percent) }}>
                        {Math.round(role.match_percent)}%
                      </span>
                    </div>
                    <ScoreBar score={role.match_percent} />
                    <p className="text-xs text-ink/55 dark:text-paper/55 mt-3">{role.blurb}</p>
                    <p className="text-sm text-ink/75 dark:text-paper/75 mt-2.5">{role.why}</p>

                    {role.matching_skills?.length > 0 && (
                      <div className="mt-3">
                        <p className="label-eyebrow mb-1.5">Relevant skills found</p>
                        <div className="flex flex-wrap gap-1.5">
                          {role.matching_skills.slice(0, 8).map((s) => (
                            <span key={s} className="text-xs bg-sage-100 text-sage-600 dark:bg-sage-500/20 dark:text-sage-100 rounded px-2 py-0.5">{s}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {role.missing_skills?.length > 0 && (
                      <div className="mt-3">
                        <p className="label-eyebrow mb-1.5">Worth strengthening</p>
                        <div className="flex flex-wrap gap-1.5">
                          {role.missing_skills.map((s) => (
                            <span key={s} className="text-xs bg-black/5 dark:bg-white/10 rounded px-2 py-0.5">{s}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    <p className="text-xs text-ink/55 dark:text-paper/55 mt-3">{role.experience_note}</p>

                    {role.next_steps?.length > 0 && (
                      <ul className="mt-3 space-y-1">
                        {role.next_steps.map((s, i) => (
                          <li key={i} className="text-xs text-brand-600 dark:text-brand-300 flex gap-1.5">
                            <ArrowRight className="h-3 w-3 mt-0.5 shrink-0" />{s}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </section>
          </Reveal>

          {/* Skill gap */}
          <Reveal>
            <section>
              <SectionHeading
                icon={Target} title="Skill Gap Analysis"
                description="Your detected skills compared against what the target job description asks for."
              />
              <div className="grid md:grid-cols-3 gap-4">
                <div className="card p-5">
                  <p className="label-eyebrow mb-3">Skills You Have</p>
                  <div className="flex flex-wrap gap-1.5">
                    {(gap.have || []).length ? gap.have.map((s) => (
                      <span key={s} className="text-xs bg-sage-100 text-sage-600 dark:bg-sage-500/20 dark:text-sage-100 rounded px-2 py-0.5">{s}</span>
                    )) : <span className="text-xs text-ink/40">None detected</span>}
                  </div>
                </div>
                <div className="card p-5">
                  <p className="label-eyebrow mb-3">Required by This Job</p>
                  <div className="flex flex-wrap gap-1.5">
                    {(gap.required_by_job || []).length ? gap.required_by_job.map((s) => (
                      <span key={s} className={`text-xs rounded px-2 py-0.5 ${
                        (gap.have || []).includes(s)
                          ? 'bg-sage-100 text-sage-600 dark:bg-sage-500/20 dark:text-sage-100'
                          : 'bg-black/5 dark:bg-white/10'
                      }`}>{s}</span>
                    )) : <span className="text-xs text-ink/40">None detected</span>}
                  </div>
                </div>
                <div className="card p-5">
                  <p className="label-eyebrow mb-3">Missing / Worth Strengthening</p>
                  <div className="flex flex-wrap gap-1.5">
                    {(gap.missing_required || []).length ? gap.missing_required.map((s) => (
                      <span key={s} className="text-xs bg-rose-100 text-rose-600 dark:bg-rose-500/20 dark:text-rose-100 rounded px-2 py-0.5">{s}</span>
                    )) : <span className="text-xs text-sage-600">You cover all required skills.</span>}
                  </div>
                </div>
              </div>
              {gap.parser_caveat && (
                <p className="mt-3 text-xs text-ink/50 dark:text-paper/50 flex items-start gap-2">
                  <Info className="h-3.5 w-3.5 mt-0.5 shrink-0" />{gap.parser_caveat}
                </p>
              )}
            </section>
          </Reveal>

          {/* Improvement plan */}
          <Reveal>
            <section>
              <SectionHeading
                icon={Lightbulb} title="Your Improvement Plan"
                description="Specific fixes based on what we found in your resume, highest impact first."
              />
              <div className="space-y-3">
                {(report.tips || []).map((tip, i) => (
                  <div key={i} className="card p-5">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <h3 className="font-display text-base">{i + 1}. {tip.title}</h3>
                      <span className={`text-xs rounded px-2 py-0.5 shrink-0 ${PRIORITY_STYLES[tip.priority]}`}>
                        {tip.priority}
                      </span>
                    </div>
                    <dl className="space-y-1.5 text-sm">
                      <div><dt className="label-eyebrow inline">Issue — </dt><dd className="inline text-ink/75 dark:text-paper/75">{tip.issue}</dd></div>
                      <div><dt className="label-eyebrow inline">Why it matters — </dt><dd className="inline text-ink/75 dark:text-paper/75">{tip.why}</dd></div>
                      <div><dt className="label-eyebrow inline">Fix — </dt><dd className="inline text-ink/75 dark:text-paper/75">{tip.fix}</dd></div>
                    </dl>

                    {(tip.before || tip.after) && (
                      <div className="mt-4 grid sm:grid-cols-2 gap-3">
                        {tip.before && (
                          <div className="rounded border border-rose-500/30 bg-rose-100/40 dark:bg-rose-500/10 p-3">
                            <p className="label-eyebrow mb-1.5">Before (from your resume)</p>
                            <p className="text-xs leading-relaxed">{tip.before}</p>
                          </div>
                        )}
                        {tip.after && (
                          <div className="rounded border border-sage-500/30 bg-sage-100/40 dark:bg-sage-500/10 p-3">
                            <p className="label-eyebrow mb-1.5">After (suggested)</p>
                            <p className="text-xs leading-relaxed">{tip.after}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          </Reveal>

          {/* Disclaimer */}
          <Reveal>
            <div className="card p-5 flex items-start gap-3">
              <Info className="h-4 w-4 text-ink/40 shrink-0 mt-0.5" />
              <p className="text-xs leading-relaxed text-ink/60 dark:text-paper/60">{report.disclaimer}</p>
            </div>
          </Reveal>

          <div className="flex flex-col sm:flex-row gap-3">
            <Link to="/analyze" className="btn-primary">Analyze another resume</Link>
            <Link to="/reports" className="btn-secondary">View all my reports</Link>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
