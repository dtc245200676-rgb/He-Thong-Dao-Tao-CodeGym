import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const TOKEN_KEY = 'access_token'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token: string) => localStorage.setItem(TOKEN_KEY, token)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean }
let refreshPromise: Promise<string> | null = null

async function refreshAccessToken(oldToken: string): Promise<string> {
  if (!refreshPromise) {
    refreshPromise = axios
      .post(`${API_BASE_URL}/api/auth/refresh`, {}, { headers: { Authorization: `Bearer ${oldToken}` } })
      .then((response) => {
        const newToken = response.data.access_token as string
        setToken(newToken)
        return newToken
      })
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

function redirectToLogin() {
  clearToken()
  sessionStorage.setItem('auth_notice', 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.')
  sessionStorage.setItem('return_path', window.location.pathname + window.location.search)
  window.dispatchEvent(new Event('auth:expired'))
  if (!window.location.pathname.startsWith('/login')) {
    window.location.assign('/login?reason=session-expired')
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as RetryConfig | undefined
    const status = error.response?.status
    const url = config?.url || ''
    const oldToken = getToken()

    if (
      status === 401 &&
      config &&
      !config._retry &&
      oldToken &&
      !url.includes('/api/auth/login') &&
      !url.includes('/api/auth/refresh')
    ) {
      config._retry = true
      try {
        const newToken = await refreshAccessToken(oldToken)
        config.headers.Authorization = `Bearer ${newToken}`
        return api(config)
      } catch {
        redirectToLogin()
      }
    }
    return Promise.reject(error)
  },
)

export function apiErrorMessage(error: unknown, fallback = 'Có lỗi xảy ra. Vui lòng thử lại.') {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (detail && typeof detail.message === 'string') return detail.message
  }
  return fallback
}
