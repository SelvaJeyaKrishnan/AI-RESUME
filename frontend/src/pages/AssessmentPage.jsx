import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { CheckCircle2, Lightbulb, ArrowRight, MessageSquareText, Sparkles } from 'lucide-react'
import { PageLoader, Spinner } from '../components/Loaders.jsx'
import {
  getCareerAssessment, submitAssessmentAnswer, completeAssessment,
} from '../services/api.js'

export default function AssessmentPage() {
  const { reportId } = useParams()
  const navigate = useNavigate()

  const [questions, setQuestions] = useState(null)
  const [index, setIndex] = useState(0)
  const [selected, setSelected] = useState(null)
  const [feedback, setFeedback] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [finishing, setFinishing] = useState(false)
  const [results, setResults] = useState([])
  const [summary, setSummary] = useState(null)
  const [loadError, setLoadError] = useState(null)

  useEffect(() => {
    getCareerAssessment(reportId)
      .then(({ data }) => {
        if (data.completed) {
          // Already done — send them straight to the report
          navigate(`/report/${reportId}`, { replace: true })
          return
        }
        setQuestions(data.questions)
        // Resume mid-assessment if they refreshed
        if (data.answered > 0 && data.answered < data.total) setIndex(data.answered)
      })
      .catch((err) => {
        setLoadError(
          err.response?.status === 404
            ? "We couldn't find that assessment. Try starting a new analysis."
            : 'Could not load your assessment. Please check your connection and refresh.'
        )
      })
  }, [reportId, navigate])

  const current = questions?.[index]
  const isLast = questions && index === questions.length - 1

  const onSelect = async (optionId) => {
    if (feedback || submitting) return       // prevents double submission
    setSelected(optionId)
    setSubmitting(true)
    try {
      const { data } = await submitAssessmentAnswer(reportId, current.id, optionId)
      setFeedback(data)
      setResults((r) => [...r, { skill: data.skill, correct: data.correct }])
    } catch (err) {
      if (err.response?.status === 409) {
        // Already answered (e.g. double-click or refresh) — move on gracefully
        toast('You already answered this one — moving on.', { icon: 'ℹ️' })
        goNext()
      } else {
        toast.error('Could not submit that answer. Please try again.')
        setSelected(null)
      }
    } finally {
      setSubmitting(false)
    }
  }

  const goNext = () => {
    setFeedback(null)
    setSelected(null)
    setIndex((i) => i + 1)
  }

  const onFinish = async () => {
    if (finishing) return
    setFinishing(true)
    try {
      const { data } = await completeAssessment(reportId)
      setSummary(data)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not finish the assessment.')
      setFinishing(false)
    }
  }

  if (loadError) {
    return (
      <div className="container-page py-20 max-w-lg text-center">
        <p className="text-rose-600 mb-4">{loadError}</p>
        <button className="btn-primary" onClick={() => navigate('/analyze')}>Start a new analysis</button>
      </div>
    )
  }

  if (!questions) return <PageLoader label="Preparing your communication challenge…" />

  // ---------- Completion summary ----------
  if (summary) {
    return (
      <div className="container-page py-16 max-w-xl">
        <motion.div
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          className="card p-8 text-center"
        >
          <div className="flex justify-center mb-5">
            <div className="h-14 w-14 rounded-full bg-sage-100 dark:bg-sage-500/20 flex items-center justify-center">
              <CheckCircle2 className="h-7 w-7 text-sage-600" />
            </div>
          </div>

          <h1 className="font-display text-2xl mb-2">Communication Assessment Complete</h1>

          <div className="flex items-center justify-center gap-8 my-7">
            <div>
              <p className="font-display text-4xl">{summary.correct}/{summary.total}</p>
              <p className="label-eyebrow mt-1">Score</p>
            </div>
            <div className="h-12 w-px bg-line dark:bg-lineDark" />
            <div>
              <p className="font-display text-4xl">{summary.accuracy}%</p>
              <p className="label-eyebrow mt-1">Accuracy</p>
            </div>
          </div>

          <p className="text-sm leading-relaxed text-ink/70 dark:text-paper/70 mb-6">{summary.message}</p>

          {results.length > 0 && (
            <div className="text-left border-t border-line dark:border-lineDark pt-5 mb-6">
              <p className="label-eyebrow mb-3">Areas covered</p>
              <div className="space-y-1.5">
                {results.map((r, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span className="text-ink/70 dark:text-paper/70">{r.skill}</span>
                    <span className={r.correct ? 'text-sage-600' : 'text-amber-600'}>
                      {r.correct ? 'Correct' : 'Review'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button className="btn-primary btn-lg w-full" onClick={() => navigate(`/report/${reportId}`)}>
            <Sparkles className="h-4 w-4" /> Reveal My Career Report
          </button>
        </motion.div>
      </div>
    )
  }

  // ---------- Question flow ----------
  const progressPct = ((index + (feedback ? 1 : 0)) / questions.length) * 100

  return (
    <div className="container-page py-10 sm:py-14 max-w-2xl">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-3">
          <MessageSquareText className="h-4 w-4 text-brand-600 dark:text-brand-300" />
          <p className="label-eyebrow">Career assessment</p>
        </div>
        <h1 className="font-display text-2xl sm:text-3xl tracking-tight mb-2">
          Before We Reveal Your Career Report…
        </h1>
        <p className="text-ink/65 dark:text-paper/65 text-sm leading-relaxed">
          Let's complete a quick communication challenge. This short assessment checks basic English
          grammar and professional communication — the kind that matters in interviews and workplace
          messages. It becomes part of your final report.
        </p>
      </div>

      {/* Progress */}
      <div className="mb-6">
        <div className="flex justify-between text-xs mb-2">
          <span className="font-medium">Question {index + 1} of {questions.length}</span>
          <span className="text-ink/45 dark:text-paper/45">{current?.skill}</span>
        </div>
        <div className="h-1.5 rounded-full bg-black/8 dark:bg-white/10 overflow-hidden">
          <motion.div
            className="h-full bg-brand-500 rounded-full"
            initial={false}
            animate={{ width: `${progressPct}%` }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          />
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={index}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.28 }}
          className="card p-6 sm:p-7"
        >
          <h2 className="font-display text-lg sm:text-xl mb-5 leading-snug">{current.prompt}</h2>

          <div className="space-y-2.5">
            {current.options.map((opt) => {
              const isSelected = selected === opt.id
              const isCorrectAnswer = feedback && opt.id === feedback.correct_option_id
              const isWrongPick = feedback && isSelected && !feedback.correct

              return (
                <button
                  key={opt.id}
                  onClick={() => onSelect(opt.id)}
                  disabled={!!feedback || submitting}
                  className={`w-full text-left rounded-md border px-4 py-3 text-sm transition-colors flex items-start gap-3
                    ${isCorrectAnswer
                      ? 'border-sage-500 bg-sage-100/60 dark:bg-sage-500/15'
                      : isWrongPick
                        ? 'border-rose-500 bg-rose-100/60 dark:bg-rose-500/15'
                        : isSelected
                          ? 'border-brand-500'
                          : 'border-line dark:border-lineDark hover:border-brand-300'}
                    ${feedback ? 'cursor-default' : 'cursor-pointer'}`}
                >
                  <span className="font-mono text-xs text-ink/40 dark:text-paper/40 mt-0.5 shrink-0 uppercase">
                    {opt.id}
                  </span>
                  <span className="flex-1">{opt.text}</span>
                  {submitting && isSelected && <Spinner className="h-4 w-4 shrink-0" />}
                </button>
              )
            })}
          </div>

          {/* Feedback */}
          <AnimatePresence>
            {feedback && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className={`mt-5 rounded-md border p-4 ${
                  feedback.correct
                    ? 'border-sage-500/40 bg-sage-100/40 dark:bg-sage-500/10'
                    : 'border-amber-400/40 bg-amber-400/10'
                }`}>
                  <p className="font-medium text-sm mb-2 flex items-center gap-2">
                    {feedback.correct
                      ? <><span aria-hidden="true">🎉</span> Correct! Great job.</>
                      : <><Lightbulb className="h-4 w-4 text-amber-600" /> Keep learning — this is an area you can improve.</>}
                  </p>

                  {!feedback.correct && (
                    <p className="text-sm text-ink/70 dark:text-paper/70 mb-2">
                      The stronger answer was: <span className="font-medium">{feedback.correct_option_text}</span>
                    </p>
                  )}

                  <p className="text-sm leading-relaxed text-ink/70 dark:text-paper/70">
                    {feedback.explanation}
                  </p>
                </div>

                <div className="mt-5 flex justify-end">
                  {isLast ? (
                    <button className="btn-primary" onClick={onFinish} disabled={finishing}>
                      {finishing ? <Spinner className="h-4 w-4" /> : null}
                      Finish assessment <ArrowRight className="h-4 w-4" />
                    </button>
                  ) : (
                    <button className="btn-primary" onClick={goNext}>
                      Next question <ArrowRight className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </AnimatePresence>

      <p className="mt-5 text-xs text-ink/45 dark:text-paper/45 text-center">
        Five questions — this is a short check, not a definitive measure of your communication ability.
      </p>
    </div>
  )
}
