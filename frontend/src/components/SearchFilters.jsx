import { MapPin, RotateCcw, Search } from 'lucide-react'

export default function SearchFilters({ filters, onChange, onSubmit, onClear, loading }) {
  return (
    <form className="search-panel" onSubmit={onSubmit}>
      <div className="search-heading">
        <div>
          <p className="eyebrow">Opportunity explorer</p>
          <h1>Find your next <em>signal.</em></h1>
          <p className="search-copy">Search the live JobPulse index by company and location.</p>
        </div>
        <span className="live-indicator"><span /> Live API</span>
      </div>
      <div className="filter-grid">
        <label className="field keyword-field">
          <span>Keyword <small>local preview</small></span>
          <input value={filters.keyword} onChange={(event) => onChange('keyword', event.target.value)} placeholder="e.g. Data Engineer" />
        </label>
        <label className="field">
          <span>Company</span>
          <input value={filters.company} onChange={(event) => onChange('company', event.target.value)} placeholder="e.g. Acme" />
        </label>
        <label className="field field-with-icon">
          <span>Location</span>
          <div><MapPin size={16} /><input value={filters.location} onChange={(event) => onChange('location', event.target.value)} placeholder="e.g. Remote" /></div>
        </label>
        <div className="filter-actions">
          <button className="button button-primary" type="submit" disabled={loading}><Search size={17} /> {loading ? 'Searching' : 'Search jobs'}</button>
          <button className="button button-quiet" type="button" onClick={onClear}><RotateCcw size={16} /> Clear</button>
        </div>
      </div>
      <p className="field-note">Keyword search will connect to the backend when title filtering is available. For now it narrows the loaded results in your browser.</p>
    </form>
  )
}
