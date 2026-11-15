import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('course_management_token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as Record<string, unknown> | undefined
    if (data) {
      const detail = data.detail ?? data.Error ?? data.error
      if (typeof detail === 'string') return detail
      if (detail && typeof detail === 'object') return flattenErrors(detail as Record<string, unknown>)
      return flattenErrors(data)
    }
    if (error.code === 'ECONNABORTED') return '请求超时，请稍后重试'
    return '无法连接服务器，请确认 Django 后端已经启动'
  }
  return error instanceof Error ? error.message : '发生未知错误'
}

function flattenErrors(data: Record<string, unknown>): string {
  return Object.entries(data)
    .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join('、') : typeof value === 'object' && value ? flattenErrors(value as Record<string, unknown>) : String(value)}`)
    .join('；')
}

export interface PageResult<T> {
  results: T[]
  count: number
  next: string | null
  previous: string | null
}

export async function fetchPage<T>(url: string, params?: Record<string, unknown>): Promise<PageResult<T>> {
  const { data } = await api.get(url, { params })
  if (Array.isArray(data)) return { results: data as T[], count: data.length, next: null, previous: null }
  return {
    results: Array.isArray(data.results) ? data.results as T[] : [],
    count: Number(data.count ?? 0),
    next: data.next ?? null,
    previous: data.previous ?? null,
  }
}
