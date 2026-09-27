const API_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')

async function request(path) {
  let response
  try {
    response = await fetch(`${API_URL}${path}`)
  } catch {
    const error = new Error('The FastAPI service could not be reached')
    error.status = 0
    throw error
  }
  if (!response.ok) {
    const error = new Error(`Request failed with status ${response.status}`)
    error.status = response.status
    throw error
  }
  return response.json()
}

export function fetchJobs({ company, location }) {
  const params = new URLSearchParams()
  if (company.trim()) params.set('company', company.trim())
  if (location.trim()) params.set('location', location.trim())
  const query = params.toString()
  return request(`/jobs${query ? `?${query}` : ''}`)
}

export function fetchJob(jobId) {
  return request(`/jobs/${jobId}`)
}

export { API_URL }
