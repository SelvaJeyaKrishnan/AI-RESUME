import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ScanSearch } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'

const PHASES = [
  'Preparing your AI career workspace…',
  'Loading analysis engine…',
]

export default function WelcomeTransition() {
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [phase, setPhase] = useState(0)

  const destination = location.state?.next || '/analyze'
  const firstName = (user?.full_name || '').split(' ')[0] || null

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { replace: true })
      return
    }

    // Respect reduced-motion and skip straight through
    const prefersReduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    if (prefersReduced) {
      navigate(destination, { replace: true })
      return
    }

    const phaseTimer = setTimeout(() => setPhase(1), 900)
    const doneTimer = setTimeout(() => navigate(destination, { replace: true }), 1800)
    return () => {
      clearTimeout(phaseTimer)
      clearTimeout(doneTimer)
    }
  }, [isAuthenticated, navigate, destination])

  return (
    <div className="min-h-screen bg-ink text-paper flex items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 grid-faint opacity-40" aria-hidden="true" />

      {/* Subtle drifting particles */}
      <div className="absolute inset-0 overflow-hidden" aria-hidden="true">
        {Array.from({ length: 14 }).map((_, i) => (
          <motion.span
            key={i}
            className="absolute h-1 w-1 rounded-full bg-brand-300/40"
            style={{ left: `${(i * 7.3) % 100}%`, top: `${(i * 13.7) % 100}%` }}
            animate={{ y: [0, -28, 0], opacity: [0.2, 0.7, 0.2] }}
            transition={{ duration: 3 + (i % 4), repeat: Infinity, delay: i * 0.2, ease: 'easeInOut' }}
          />
        ))}
      </div>

      <div className="relative text-center px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="flex justify-center mb-6"
        >
          <div className="relative">
            <ScanSearch className="h-9 w-9 text-amber-400" strokeWidth={1.75} />
            <motion.div
              className="absolute -inset-3 rounded-full border border-brand-300/30"
              animate={{ scale: [1, 1.35, 1], opacity: [0.6, 0, 0.6] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
            />
          </div>
        </motion.div>

        <motion.h1
          className="font-display text-3xl sm:text-4xl mb-3"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.1 }}
        >
          {firstName ? `Welcome back, ${firstName}.` : 'Welcome back.'}
        </motion.h1>

        <motion.p
          key={phase}
          className="text-paper/60 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {PHASES[phase]}
        </motion.p>

        <div className="mt-7 mx-auto w-52 h-0.5 rounded-full bg-white/10 overflow-hidden">
          <motion.div
            className="h-full bg-amber-400"
            initial={{ width: '0%' }}
            animate={{ width: '100%' }}
            transition={{ duration: 1.7, ease: 'easeInOut' }}
          />
        </div>
      </div>
    </div>
  )
}
