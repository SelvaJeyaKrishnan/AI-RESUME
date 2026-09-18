import { motion } from 'framer-motion'
import { CountUp } from './Motion.jsx'

export const bandColor = (score) => {
  if (score >= 80) return '#3F8A5C'
  if (score >= 65) return '#D98E22'
  if (score >= 45) return '#B8721A'
  return '#B8524E'
}

export const bandLabel = (score) => {
  if (score >= 80) return 'Strong'
  if (score >= 65) return 'Good'
  if (score >= 45) return 'Fair'
  return 'Needs work'
}

export default function ScoreGauge({ score = 0, label, sublabel, size = 160, strokeWidth = 10 }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const pct = Math.min(Math.max(score, 0), 100)
  const offset = circumference - (pct / 100) * circumference
  const color = bandColor(pct)

  return (
    <div className="flex flex-col items-center">
      <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2} cy={size / 2} r={radius} fill="none"
            stroke="currentColor" strokeWidth={strokeWidth}
            className="text-black/8 dark:text-white/10"
          />
          <motion.circle
            cx={size / 2} cy={size / 2} r={radius} fill="none"
            stroke={color} strokeWidth={strokeWidth} strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className="font-display leading-none" style={{ fontSize: size * 0.26 }}>
            <CountUp value={pct} decimals={0} />
          </span>
          <span className="font-mono text-[10px] text-ink/40 dark:text-paper/40 mt-1">/ 100</span>
        </div>
      </div>
      {label && <p className="mt-3 font-medium text-sm">{label}</p>}
      <p className="text-xs mt-0.5" style={{ color }}>{sublabel || bandLabel(pct)}</p>
    </div>
  )
}
