import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api } from '../lib/api'

export type Role = 'admin' | 'teacher' | 'student'
export interface CurrentUser {
  id: number
  username: string
  email: string
  profile: null | { type: Role; name?: string; student_no?: string; age?: number; department?: string }
}
interface AuthContextValue {
  user: CurrentUser | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}
const AuthContext = createContext<AuthContextValue | null>(null)
const TOKEN_KEY = 'course_management_token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) { setUser(null); return }
    const { data } = await api.get<CurrentUser>('/auth/me/')
    setUser(data)
  }, [])

  useEffect(() => {
    refreshUser().catch(() => {
      localStorage.removeItem(TOKEN_KEY)
      setUser(null)
    }).finally(() => setLoading(false))
  }, [refreshUser])

  const login = useCallback(async (username: string, password: string) => {
    const { data } = await api.post<{ token: string }>('/auth/login/', { username, password })
    localStorage.setItem(TOKEN_KEY, data.token)
    try { await refreshUser() }
    catch (error) { localStorage.removeItem(TOKEN_KEY); throw error }
  }, [refreshUser])

  const logout = useCallback(async () => {
    try { await api.post('/auth/logout/') } finally {
      localStorage.removeItem(TOKEN_KEY)
      setUser(null)
    }
  }, [])

  const value = useMemo(() => ({ user, loading, login, logout, refreshUser }), [user, loading, login, logout, refreshUser])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used within AuthProvider')
  return value
}
