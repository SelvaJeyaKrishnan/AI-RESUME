import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts'
import StatCard from './StatCard.jsx'

const DIST_COLORS = { '0-20': '#B8524E', '21-40': '#B8524E', '41-60': '#D98E22', '61-80': '#D98E22', '81-100': '#3F8A5C' }
const REC_COLORS = {
  'Strong Match': '#3F8A5C',
  'Good Match': '#D98E22',
  'Potential Match': '#3E4A8A',
  'Low Match': '#B8524E',
}

export default function AnalyticsPanel({ analytics }) {
  const distributionData = Object.entries(analytics.score_distribution).map(([bucket, count]) => ({ bucket, count }))
  const recData = Object.entries(analytics.recommendation_breakdown).map(([rec, count]) => ({ rec, count }))
  const skillsData = analytics.top_skills.slice(0, 8).map((s) => ({ skill: s.skill, count: s.count }))

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total candidates" value={analytics.total_candidates} />
        <StatCard label="Processed resumes" value={analytics.processed_resumes} hint={analytics.failed_resumes ? `${analytics.failed_resumes} failed` : undefined} />
        <StatCard label="Shortlisted" value={analytics.shortlisted_candidates} tone="sage" />
        <StatCard label="Avg. match score" value={`${analytics.average_match_score}%`} tone="amber" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <p className="label-eyebrow mb-4">Score distribution</p>
          {distributionData.some((d) => d.count > 0) ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-black/5 dark:stroke-white/10" />
                <XAxis dataKey="bucket" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {distributionData.map((d, i) => <Cell key={i} fill={DIST_COLORS[d.bucket]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-sm text-ink/40 dark:text-paper/40 py-16 text-center">No analyzed candidates yet</p>}
        </div>

        <div className="card p-6">
          <p className="label-eyebrow mb-4">Candidates by recommendation</p>
          {recData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={recData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} className="stroke-black/5 dark:stroke-white/10" />
                <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="rec" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} width={110} />
                <Tooltip cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {recData.map((d, i) => <Cell key={i} fill={REC_COLORS[d.rec] || '#3E4A8A'} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-sm text-ink/40 dark:text-paper/40 py-16 text-center">No analyzed candidates yet</p>}
        </div>
      </div>

      <div className="card p-6">
        <p className="label-eyebrow mb-4">Top skills among candidates</p>
        {skillsData.length ? (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={skillsData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} className="stroke-black/5 dark:stroke-white/10" />
              <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="skill" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} width={110} />
              <Tooltip cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
              <Bar dataKey="count" fill="#3E4A8A" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : <p className="text-sm text-ink/40 dark:text-paper/40 py-16 text-center">No skills detected yet</p>}
      </div>
    </div>
  )
}
