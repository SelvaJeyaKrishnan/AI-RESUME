import { createContext, useContext, useState, useCallback } from 'react'
import { loginUser, registerUser } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('resumeai_user')
    return raw ? JSON.parse(raw) : null
  })

  const persist = (token, userData) => {
    localStorage.setItem('resumeai_token', token)
    localStorage.setItem('resumeai_user', JSON.stringify(userData))
    setUser(userData)
  }

  const login = useCallback(async (email, password) => {
    const { data } = await loginUser({ email, password })
    persist(data.access_token, data.user)
    return data.user
  }, [])

  const register = useCallback(async (payload) => {
    const { data } = await registerUser(payload)
    persist(data.access_token, data.user)
    return data.user
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('resumeai_token')
    localStorage.removeItem('resumeai_user')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
