import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function Pagination({ page, pageCount, onPageChange, pageSize, onPageSizeChange }) {
  return (
    <div className="pagination">
      <label>Show <select value={pageSize} onChange={(event) => onPageSizeChange(Number(event.target.value))}><option value="6">6</option><option value="12">12</option><option value="24">24</option></select> per page</label>
      <div className="page-controls"><span>Page {page} of {pageCount}</span><button className="icon-button" onClick={() => onPageChange(page - 1)} disabled={page <= 1} aria-label="Previous page"><ChevronLeft size={17} /></button><button className="icon-button" onClick={() => onPageChange(page + 1)} disabled={page >= pageCount} aria-label="Next page"><ChevronRight size={17} /></button></div>
    </div>
  )
}
