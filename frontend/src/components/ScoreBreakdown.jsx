const DIMENSIONS = [
  { key: 'skills_score', label: 'Skills' },
  { key: 'experience_score', label: 'Experience' },
  { key: 'semantic_score', label: 'Semantic fit' },
  { key: 'education_score', label: 'Education' },
  { key: 'keyword_score', label: 'Keywords' },
]

export default function ScoreBreakdown({ analysis }) {
  return (
    <div className="space-y-3">
      {DIMENSIONS.map(({ key, label }) => {
        const value = analysis[key]
        return (
          <div key={key}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-ink/60 dark:text-paper/60">{label}</span>
              <span className="font-mono">{Math.round(value)}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-black/5 dark:bg-white/10 overflow-hidden">
              <div
                className="h-full rounded-full bg-brand-500"
                style={{ width: `${Math.min(Math.max(value, 0), 100)}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
