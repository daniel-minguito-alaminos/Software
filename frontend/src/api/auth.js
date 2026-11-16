// Calls to the backend authentication endpoints (BIZ-32).
// The session lives in an HttpOnly cookie set by the backend; JavaScript
// never reads or stores the token.

const API_BASE = '/api'

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

const UNREACHABLE = 'The server is not available right now. Please try again later.'
const GENERIC = 'Something went wrong. Please try again.'

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    throw new ApiError(UNREACHABLE, 0)
  }

  if (!response.ok) {
    let message = response.status >= 500 ? UNREACHABLE : GENERIC
    try {
      const data = await response.json()
      if (typeof data.detail === 'string') message = data.detail
    } catch {
      // No JSON body (e.g. the dev proxy cannot reach the backend).
    }
    throw new ApiError(message, response.status)
  }

  return response.status === 204 ? null : response.json()
}

export function login(email, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function logout() {
  return request('/auth/logout', { method: 'POST' })
}

// Returns the logged-in user, or null when there is no valid session.
export async function getCurrentUser() {
  try {
    return await request('/auth/me')
  } catch (error) {
    if (error.status === 401) return null
    throw error
  }
}
