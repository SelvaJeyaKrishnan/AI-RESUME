import ScoreRing from './ScoreRing.jsx'
import RecommendationBadge from './RecommendationBadge.jsx'

const ROWS = [
  { label: 'Match score', render: (c) => <ScoreRing score={c.analysis.overall_score} size={44} strokeWidth={4} /> },
  { label: 'Recommendation', render: (c) => <RecommendationBadge recommendation={c.analysis.recommendation} /> },
  { label: 'Experience', render: (c) => `${c.candidate?.years_of_experience ?? 0} years` },
  {
    label: 'Education',
    render: (c) => c.candidate?.education?.[0]?.degree_line || 'Not detected',
  },
  {
    label: 'Matching skills',
    render: (c) => (
      <div className="flex flex-wrap gap-1">
        {c.analysis.matching_skills.slice(0, 8).map((s) => (
          <span key={s} className="text-xs bg-sage-100 text-sage-600 dark:bg-sage-500/20 dark:text-sage-100 rounded px-1.5 py-0.5">{s}</span>
        ))}
      </div>
    ),
  },
  {
    label: 'Missing skills',
    render: (c) => (
      <div className="flex flex-wrap gap-1">
        {c.analysis.missing_skills.length
          ? c.analysis.missing_skills.map((s) => (
              <span key={s} className="text-xs bg-rose-100 text-rose-600 dark:bg-rose-500/20 dark:text-rose-100 rounded px-1.5 py-0.5">{s}</span>
            ))
          : <span className="text-xs text-ink/40 dark:text-paper/40">None</span>}
      </div>
    ),
  },
]

export default function ComparisonTable({ candidates }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr>
            <th className="text-left label-eyebrow pb-3 pr-4 align-bottom">Category</th>
            {candidates.map((c) => (
              <th key={c.resume_id} className="text-left pb-3 px-4 align-bottom font-medium">
                {c.candidate?.full_name || c.original_filename}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ROWS.map((row) => (
            <tr key={row.label} className="border-t border-line dark:border-lineDark">
              <td className="py-3 pr-4 text-ink/50 dark:text-paper/50 whitespace-nowrap">{row.label}</td>
              {candidates.map((c) => (
                <td key={c.resume_id} className="py-3 px-4 align-top">{row.render(c)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
