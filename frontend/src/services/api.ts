import type {
  Analysis,
  AuthUser,
  Location,
  LocationHourlyStatistics,
  LocationPayload,
  Project,
  ProjectPayload,
  Statistics,
  Violation,
} from '../types'

export const API_BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')
export const API_ORIGIN = API_BASE.replace(/\/api$/, '')
const TOKEN_KEY = 'helmet_auth_token'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setAuthToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

function errorMessage(detail: unknown, fallback: string) {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => (typeof item === 'object' && item && 'msg' in item ? String(item.msg) : String(item)))
      .join('\n')
  }
  return fallback
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAuthToken()
  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        ...(init?.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...init?.headers,
      },
    })
  } catch {
    throw new ApiError(
      'Không kết nối được máy chủ API. Hãy chạy backend (cổng 8000), rồi tải lại trang đăng ký.',
      0,
    )
  }
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith('/auth/')) {
      window.dispatchEvent(new Event('auth:expired'))
    }
    let message = `Yêu cầu thất bại (${response.status})`
    try {
      const body = (await response.json()) as { detail?: unknown }
      message = errorMessage(body.detail, message)
    } catch {
      // Keep fallback message.
    }
    throw new ApiError(message, response.status)
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

function downloadUrl(path: string) {
  const token = getAuthToken()
  const suffix = token ? `?access_token=${encodeURIComponent(token)}` : ''
  return `${API_BASE}${path}${suffix}`
}

export function assetUrl(path?: string | null): string {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  return `${API_ORIGIN}${path}`
}

export const api = {
  health: () => request<{ status: string; model_exists: boolean }>('/health'),
  register: (payload: { username: string; password: string }) =>
    request<{ access_token: string; user: AuthUser }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  login: (payload: { username: string; password: string }) =>
    request<{ access_token: string; user: AuthUser }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  me: () => request<AuthUser>('/auth/me'),

  projects: () => request<Project[]>('/projects'),
  project: (id: number) => request<Project>(`/projects/${id}`),
  createProject: (payload: ProjectPayload) =>
    request<Project>('/projects', { method: 'POST', body: JSON.stringify(payload) }),
  updateProject: (id: number, payload: Partial<ProjectPayload>) =>
    request<Project>(`/projects/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteProject: (id: number) => request<void>(`/projects/${id}`, { method: 'DELETE' }),

  location: (id: number) => request<Location>(`/locations/${id}`),
  locations: (projectId: number) => request<Location[]>(`/projects/${projectId}/locations`),
  createLocation: (projectId: number, payload: LocationPayload) =>
    request<Location>(`/projects/${projectId}/locations`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateLocation: (id: number, payload: Partial<LocationPayload>) =>
    request<Location>(`/locations/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteLocation: (id: number) => request<void>(`/locations/${id}`, { method: 'DELETE' }),

  analyses: (params?: { project_id?: number; location_id?: number; limit?: number }) => {
    const search = new URLSearchParams()
    if (params?.project_id) search.set('project_id', String(params.project_id))
    if (params?.location_id) search.set('location_id', String(params.location_id))
    if (params?.limit) search.set('limit', String(params.limit))
    const suffix = search.size ? `?${search.toString()}` : ''
    return request<Analysis[]>(`/analyses${suffix}`)
  },
  analysis: (id: number) => request<Analysis>(`/analyses/${id}`),
  allAnalyses: async (): Promise<Analysis[]> => {
    const rows: Analysis[] = []
    for (let offset = 0; ; offset += 500) {
      const page = await request<Analysis[]>(`/analyses?limit=500&offset=${offset}`)
      rows.push(...page)
      if (page.length < 500) return rows
    }
  },
  createAnalysis: (formData: FormData) =>
    request<Analysis>('/analyses', { method: 'POST', body: formData }),

  locationStatistics: (id: number) => request<Statistics>(`/locations/${id}/statistics`),
  locationHourlyStatistics: (id: number) => request<LocationHourlyStatistics>(`/locations/${id}/hourly-statistics`),
  projectStatistics: (id: number) => request<Statistics>(`/projects/${id}/statistics`),
  locationViolations: (id: number, limit = 200) =>
    request<Violation[]>(`/locations/${id}/violations?limit=${limit}`),

  downloadAnalysisUrl: (id: number) => downloadUrl(`/downloads/analyses/${id}`),
  downloadLocationUrl: (id: number) => downloadUrl(`/downloads/locations/${id}`),
  downloadProjectUrl: (id: number) => downloadUrl(`/downloads/projects/${id}`),
}
