import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ScanSearch, FileSearch, Sparkles, Target, MessageSquareText, Lightbulb,
  Compass, Upload, ClipboardList, CheckCircle2, ArrowRight, Menu, X, Sun, Moon,
} from 'lucide-react'
import { Reveal } from '../components/Motion.jsx'
import { useTheme } from '../context/ThemeContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'

const FEATURES = [
  { icon: FileSearch, title: 'ATS Resume Analysis', body: 'See how an applicant tracking system actually parses your resume, factor by factor — structure, formatting, keywords and more.' },
  { icon: Sparkles, title: 'AI Resume Review', body: 'An overall rating broken into skills, experience, education, projects, content quality and job alignment — each one explained.' },
  { icon: Target, title: 'Job Eligibility Matching', body: 'Compare your resume against the role you actually want, and see suitable roles ranked by how well your real skills align.' },
  { icon: MessageSquareText, title: 'Communication Assessment', body: 'A short grammar and professional-communication check covering the kind of writing that shows up in interviews and at work.' },
  { icon: Lightbulb, title: 'Personalised Improvement Tips', body: 'Specific fixes drawn from your own resume text, with before-and-after rewrites of your actual bullet points.' },
  { icon: Compass, title: 'Career Recommendations', body: 'Role suggestions built from the skills detected in your resume, with the gaps to close before you apply.' },
]

const STEPS = [
  { icon: Upload, title: 'Upload Your Resume', body: 'Drop in a PDF or DOCX. We extract your skills, experience, education and projects.' },
  { icon: Target, title: 'Describe Your Target Job', body: 'Paste the job description you are aiming for so the analysis is measured against a real role.' },
  { icon: ClipboardList, title: 'Complete the Communication Challenge', body: 'Five short questions on grammar and professional communication, with feedback on every answer.' },
  { icon: CheckCircle2, title: 'Get Your AI Career Report', body: 'ATS score, resume rating, role matches, skill gaps and a prioritised improvement plan.' },
]

const EVALUATES = [
  'Resume structure', 'ATS compatibility', 'Skills', 'Experience', 'Education',
  'Keywords', 'Job relevance', 'Communication', 'Grammar',
]

function HeroVisual() {
  // A restrained "scanning" animation that reflects what the product does:
  // reading a document line by line and surfacing structured signals.
  return (
    <div className="relative surface-raised p-6 overflow-hidden shadow-pop" aria-hidden="true">
      <div className="flex items-center gap-2 mb-5">
        <div className="h-2 w-2 rounded-full bg-rose-500/60" />
        <div className="h-2 w-2 rounded-full bg-amber-400/60" />
        <div className="h-2 w-2 rounded-full bg-sage-500/60" />
        <span className="ml-2 font-mono text-[11px] text-ink/40 dark:text-paper/40">resume.pdf</span>
      </div>

      <div className="space-y-2.5 relative">
        {[92, 74, 86, 60, 80, 68, 90, 55].map((w, i) => (
          <motion.div
            key={i}
            className="h-2 rounded bg-black/8 dark:bg-white/10"
            style={{ width: `${w}%` }}
            initial={{ opacity: 0.35 }}
            animate={{ opacity: [0.35, 0.85, 0.35] }}
            transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.18, ease: 'easeInOut' }}
          />
        ))}

        {/* Scanning line */}
        <motion.div
          className="absolute left-0 right-0 h-px bg-brand-500/70"
          initial={{ top: 0 }}
          animate={{ top: ['0%', '100%', '0%'] }}
          transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div className="h-8 -mt-8 bg-gradient-to-b from-transparent to-brand-500/10" />
        </motion.div>
      </div>

      <div className="mt-6 pt-5 border-t border-line dark:border-lineDark grid grid-cols-3 gap-3">
        {[
          { label: 'ATS', value: '87' },
          { label: 'Skills', value: '12' },
          { label: 'Match', value: '81%' },
        ].map((chip, i) => (
          <motion.div
            key={chip.label}
            className="text-center"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 + i * 0.15, duration: 0.5 }}
          >
            <p className="font-display text-xl">{chip.value}</p>
            <p className="label-eyebrow">{chip.label}</p>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default function LandingPage() {
  const { theme, toggleTheme } = useTheme()
  const { isAuthenticated } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)

  const primaryTo = isAuthenticated ? '/analyze' : '/register'

  const navLinks = [
    { href: '#features', label: 'Features' },
    { href: '#how-it-works', label: 'How It Works' },
    { href: '#about', label: 'About' },
  ]

  return (
    <div className="min-h-screen bg-paper dark:bg-ink text-ink dark:text-paper">
      {/* Navbar */}
      <header className="sticky top-0 z-40 border-b border-line dark:border-lineDark bg-paper/85 dark:bg-ink/85 backdrop-blur">
        <div className="container-page flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <ScanSearch className="h-5 w-5 text-brand-600 dark:text-brand-300" strokeWidth={2} />
            <span className="font-display text-lg tracking-tight">ResumeAI</span>
          </Link>

          <nav className="hidden md:flex items-center gap-7 text-sm">
            {navLinks.map((l) => (
              <a key={l.href} href={l.href} className="text-ink/70 dark:text-paper/70 hover:text-ink dark:hover:text-paper transition-colors">
                {l.label}
              </a>
            ))}
          </nav>

          <div className="hidden md:flex items-center gap-2">
            <button onClick={toggleTheme} className="btn-ghost !px-2" aria-label="Toggle theme">
              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            {isAuthenticated ? (
              <Link to="/analyze" className="btn-primary">Open workspace</Link>
            ) : (
              <>
                <Link to="/login" className="btn-ghost">Login</Link>
                <Link to="/register" className="btn-primary">Get Started</Link>
              </>
            )}
          </div>

          <button className="md:hidden btn-ghost !px-2" onClick={() => setMenuOpen((o) => !o)} aria-label="Menu">
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {menuOpen && (
          <div className="md:hidden border-t border-line dark:border-lineDark px-5 py-4 space-y-3">
            {navLinks.map((l) => (
              <a key={l.href} href={l.href} onClick={() => setMenuOpen(false)} className="block text-sm text-ink/70 dark:text-paper/70">
                {l.label}
              </a>
            ))}
            <div className="flex gap-2 pt-2">
              <Link to="/login" className="btn-secondary flex-1">Login</Link>
              <Link to={primaryTo} className="btn-primary flex-1">Get Started</Link>
            </div>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="bg-hero-wash">
        <div className="container-page py-16 sm:py-24 grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <div>
            <Reveal>
              <p className="label-eyebrow mb-4">AI career assessment</p>
            </Reveal>
            <Reveal delay={0.06}>
              <h1 className="font-display text-4xl sm:text-5xl lg:text-[3.4rem] leading-[1.08] tracking-tight">
                Turn Your Resume Into Your Career Advantage.
              </h1>
            </Reveal>
            <Reveal delay={0.12}>
              <p className="mt-5 text-lg leading-relaxed text-ink/70 dark:text-paper/70 max-w-xl">
                Analyze your resume, test your communication skills, discover suitable career
                opportunities, and get an actionable improvement plan — all in one place.
              </p>
            </Reveal>
            <Reveal delay={0.18}>
              <div className="mt-8 flex flex-col sm:flex-row gap-3">
                <Link to={primaryTo} className="btn-primary btn-lg">
                  Analyze My Resume <ArrowRight className="h-4 w-4" />
                </Link>
                <a href="#how-it-works" className="btn-secondary btn-lg">See How It Works</a>
              </div>
            </Reveal>
            <Reveal delay={0.24}>
              <p className="mt-5 text-xs text-ink/50 dark:text-paper/50">
                Your resume is analyzed against the job description you provide. Results are
                AI-generated guidance, not a hiring decision.
              </p>
            </Reveal>
          </div>

          <Reveal delay={0.1}>
            <HeroVisual />
          </Reveal>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="border-t border-line dark:border-lineDark">
        <div className="container-page py-16 sm:py-20">
          <Reveal>
            <p className="label-eyebrow mb-3">What you get</p>
            <h2 className="font-display text-3xl sm:text-4xl tracking-tight max-w-2xl">
              Everything your resume is judged on, measured and explained.
            </h2>
          </Reveal>

          <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURES.map((f, i) => (
              <Reveal key={f.title} delay={i * 0.06}>
                <div className="card p-6 h-full hover:border-brand-300 transition-colors">
                  <f.icon className="h-5 w-5 text-brand-600 dark:text-brand-300 mb-4" strokeWidth={1.75} />
                  <h3 className="font-display text-lg mb-2">{f.title}</h3>
                  <p className="text-sm leading-relaxed text-ink/65 dark:text-paper/65">{f.body}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="border-t border-line dark:border-lineDark bg-black/[0.015] dark:bg-white/[0.015]">
        <div className="container-page py-16 sm:py-20">
          <Reveal>
            <p className="label-eyebrow mb-3">How it works</p>
            <h2 className="font-display text-3xl sm:text-4xl tracking-tight">Four steps to your career report.</h2>
          </Reveal>

          <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {STEPS.map((s, i) => (
              <Reveal key={s.title} delay={i * 0.08}>
                <div className="card p-6 h-full relative">
                  <span className="font-mono text-xs text-ink/30 dark:text-paper/30 absolute top-5 right-5">
                    0{i + 1}
                  </span>
                  <s.icon className="h-5 w-5 text-brand-600 dark:text-brand-300 mb-4" strokeWidth={1.75} />
                  <h3 className="font-display text-base mb-2 pr-6">{s.title}</h3>
                  <p className="text-sm leading-relaxed text-ink/65 dark:text-paper/65">{s.body}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Trust / what we evaluate */}
      <section id="about" className="border-t border-line dark:border-lineDark">
        <div className="container-page py-16 sm:py-20 grid lg:grid-cols-2 gap-12">
          <Reveal>
            <p className="label-eyebrow mb-3">What we actually evaluate</p>
            <h2 className="font-display text-3xl sm:text-4xl tracking-tight mb-5">
              No black-box scores.
            </h2>
            <p className="text-ink/70 dark:text-paper/70 leading-relaxed mb-4">
              Every number in your report traces back to something measurable in your resume text
              and the job description you provide. Each factor shows what was found, why it matters,
              and what to change.
            </p>
            <p className="text-ink/70 dark:text-paper/70 leading-relaxed">
              ResumeAI is built for students, freshers, developers and job seekers who want specific,
              honest feedback rather than a vague score out of ten.
            </p>
          </Reveal>

          <Reveal delay={0.1}>
            <div className="card p-6">
              <p className="label-eyebrow mb-4">Analyzed in every report</p>
              <div className="flex flex-wrap gap-2">
                {EVALUATES.map((e) => (
                  <span key={e} className="text-sm rounded border border-line dark:border-lineDark px-3 py-1.5">
                    {e}
                  </span>
                ))}
              </div>
              <div className="mt-6 pt-5 border-t border-line dark:border-lineDark">
                <p className="text-sm text-ink/65 dark:text-paper/65 leading-relaxed">
                  Scores are AI-generated assessments meant to guide your improvements. They are not a
                  guarantee of eligibility, and they do not replace a human reviewer.
                </p>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-line dark:border-lineDark bg-hero-wash">
        <div className="container-page py-16 sm:py-20 text-center">
          <Reveal>
            <h2 className="font-display text-3xl sm:text-4xl tracking-tight mb-4">
              Find out what your resume is really saying.
            </h2>
            <p className="text-ink/70 dark:text-paper/70 mb-8 max-w-xl mx-auto">
              Upload it, name the role you want, and get a full breakdown in a couple of minutes.
            </p>
            <Link to={primaryTo} className="btn-primary btn-lg">
              Analyze My Resume <ArrowRight className="h-4 w-4" />
            </Link>
          </Reveal>
        </div>
      </section>

      <footer className="border-t border-line dark:border-lineDark">
        <div className="container-page py-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-ink/50 dark:text-paper/50">
          <div className="flex items-center gap-2">
            <ScanSearch className="h-4 w-4" />
            <span className="font-display">ResumeAI</span>
          </div>
          <p>Decision-support for your job search — not a hiring decision.</p>
        </div>
      </footer>
    </div>
  )
}
