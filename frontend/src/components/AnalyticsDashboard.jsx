import { BarChart3, Building2, Clock3, MapPinned, TrendingUp } from 'lucide-react'

const cards = [
  { label: 'Total jobs', icon: BarChart3, value: '—', note: 'Requires analytics endpoint' },
  { label: 'Jobs by company', icon: Building2, value: '—', note: 'Company distribution planned' },
  { label: 'Jobs by location', icon: MapPinned, value: '—', note: 'Location distribution planned' },
]

export default function AnalyticsDashboard({ visibleJobs }) {
  return (
    <section className="analytics-section" id="analytics">
      <div className="section-heading"><div><p className="eyebrow">Signal room</p><h2>Analytics, when your data is ready.</h2></div><span className="planned-badge">Planned capability</span></div>
      <div className="analytics-grid">
        {cards.map(({ label, icon: Icon, value, note }) => <div className="metric-card" key={label}><div className="metric-top"><span>{label}</span><Icon size={17} /></div><strong>{value}</strong><p>{note}</p></div>)}
        <div className="chart-card"><div className="metric-top"><span><Clock3 size={16} /> Recent postings</span><span className="chart-label">Preview</span></div><div className="bar-preview" aria-hidden="true"><i /><i /><i /><i /><i /></div><p>{visibleJobs.length ? `${visibleJobs.length} loaded result${visibleJobs.length === 1 ? '' : 's'} in this view` : 'Live trend data will appear here'}</p></div>
        <div className="chart-card trend-card"><div className="metric-top"><span><TrendingUp size={16} /> Posting trends</span><span className="chart-label">Coming soon</span></div><div className="empty-chart"><span>No trend endpoint yet</span></div><p>Connect an analytics endpoint to unlock time-series insights.</p></div>
      </div>
    </section>
  )
}
