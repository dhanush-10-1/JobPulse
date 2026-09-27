import { useEffect, useMemo, useState } from 'react'
import { Database, Filter, Layers3, RefreshCw } from 'lucide-react'
import Header from './components/Header'
import SearchFilters from './components/SearchFilters'
import JobCard from './components/JobCard'
import JobDetails from './components/JobDetails'
import Pagination from './components/Pagination'
import AnalyticsDashboard from './components/AnalyticsDashboard'
import { EmptyState, ErrorState, LoadingState } from './components/States'
import { fetchJobs } from './services/api'

const initialFilters = { keyword: '', company: '', location: '' }

export default function App() {
  const [filters, setFilters] = useState(initialFilters)
  const [submittedFilters, setSubmittedFilters] = useState(initialFilters)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedJob, setSelectedJob] = useState(null)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(6)

  const loadJobs = async (nextFilters = submittedFilters) => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchJobs(nextFilters)
      setJobs(Array.isArray(result) ? result : [])
    } catch (requestError) {
      if (requestError.status === 404) setJobs([])
      else setError(requestError)
    } finally { setLoading(false) }
  }

  useEffect(() => { loadJobs(initialFilters) }, [])

  const visibleJobs = useMemo(() => {
    const keyword = submittedFilters.keyword.trim().toLowerCase()
    return keyword ? jobs.filter((job) => `${job.title || ''} ${job.company || ''}`.toLowerCase().includes(keyword)) : jobs
  }, [jobs, submittedFilters.keyword])
  const pageCount = Math.max(1, Math.ceil(visibleJobs.length / pageSize))
  const pagedJobs = visibleJobs.slice((page - 1) * pageSize, page * pageSize)

  const updateFilter = (name, value) => setFilters((current) => ({ ...current, [name]: value }))
  const handleSubmit = (event) => { event.preventDefault(); setSubmittedFilters(filters); setPage(1); loadJobs(filters) }
  const clearFilters = () => { setFilters(initialFilters); setSubmittedFilters(initialFilters); setPage(1); loadJobs(initialFilters) }
  const changePageSize = (value) => { setPageSize(value); setPage(1) }

  return <div id="top" className="app-shell">
    <Header />
    <main>
      <SearchFilters filters={filters} onChange={updateFilter} onSubmit={handleSubmit} onClear={clearFilters} loading={loading} />
      <section className="jobs-section" id="jobs">
        <div className="section-heading"><div><p className="eyebrow">Live index</p><h2>Latest opportunities <span className="result-count">{loading ? '...' : visibleJobs.length}</span></h2></div><div className="section-tools"><span className="sync-label"><RefreshCw size={14} /> Synced just now</span><span className="filter-label"><Filter size={14} /> {submittedFilters.company || submittedFilters.location ? 'Filtered view' : 'All roles'}</span></div></div>
        {loading ? <LoadingState /> : error ? <ErrorState onRetry={() => loadJobs()} /> : visibleJobs.length === 0 ? <EmptyState onClear={clearFilters} /> : <>
          <div className="job-list">{pagedJobs.map((job, index) => <JobCard key={`${job.url}-${index}`} job={job} onSelect={setSelectedJob} />)}</div>
          <Pagination page={page} pageCount={pageCount} onPageChange={setPage} pageSize={pageSize} onPageSizeChange={changePageSize} />
        </>}
      </section>
      <AnalyticsDashboard visibleJobs={visibleJobs} />
    </main>
    <footer><span><span className="footer-mark"><Layers3 size={14} /></span> JobPulse</span><span><Database size={14} /> Data pipeline connected to FastAPI</span></footer>
    <JobDetails job={selectedJob} onClose={() => setSelectedJob(null)} />
  </div>
}
