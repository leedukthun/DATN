import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api, getAuthToken, setAuthToken } from '../services/api'
import type { AuthUser } from '../types'

interface AuthContextValue {
  user: AuthUser | null
  ready: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [ready, setReady] = useState(false)

  const logout = () => {
    setAuthToken(null)
    setUser(null)
  }

  useEffect(() => {
    const onExpired = () => logout()
    window.addEventListener('auth:expired', onExpired)
    return () => window.removeEventListener('auth:expired', onExpired)
  }, [])

  useEffect(() => {
    let cancelled = false
    const bootstrap = async () => {
      if (!getAuthToken()) {
        if (!cancelled) setReady(true)
        return
      }
      try {
        const me = await api.me()
        if (!cancelled) setUser(me)
      } catch {
        if (!cancelled) logout()
      } finally {
        if (!cancelled) setReady(true)
      }
    }
    void bootstrap()
    return () => {
      cancelled = true
    }
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      ready,
      login: async (username, password) => {
        const result = await api.login({ username, password })
        setAuthToken(result.access_token)
        setUser(result.user)
      },
      register: async (username, password) => {
        const result = await api.register({ username, password })
        setAuthToken(result.access_token)
        setUser(result.user)
      },
      logout,
    }),
    [user, ready],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
