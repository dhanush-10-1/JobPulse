import { AlertTriangle, Inbox, LoaderCircle, RefreshCw } from 'lucide-react'

export function LoadingState() { return <div className="state-panel"><LoaderCircle className="spin" size={24} /><h3>Loading the opportunity index</h3><p>Fetching the latest jobs from JobPulse.</p></div> }
export function EmptyState({ onClear }) { return <div className="state-panel"><span className="state-icon"><Inbox size={23} /></span><h3>No jobs found</h3><p>Try broadening your company, location, or keyword filters.</p><button className="button button-quiet" onClick={onClear}><RefreshCw size={15} /> Reset filters</button></div> }
export function ErrorState({ onRetry }) { return <div className="state-panel error-state"><span className="state-icon"><AlertTriangle size={23} /></span><h3>Could not load jobs</h3><p>The FastAPI service may be unavailable. Check that it is running and try again.</p><button className="button button-primary" onClick={onRetry}><RefreshCw size={15} /> Try again</button></div> }
