import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { authApi, tokenStorage, userApi } from '../services/api'
import type { UserRegister, UserResponse } from '../types'

interface AuthContextValue {
  user: UserResponse | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  registerAndLogin: (payload: UserRegister) => Promise<void>
  logout: () => void
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [token, setToken] = useState<string | null>(() => tokenStorage.get())
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const refreshProfile = useCallback(async () => {
    const currentToken = tokenStorage.get()
    if (!currentToken) {
      setUser(null)
      setToken(null)
      setIsLoading(false)
      return
    }

    try {
      const profile = await userApi.getMe()
      setUser(profile)
      setToken(currentToken)
    } catch {
      tokenStorage.clear()
      setUser(null)
      setToken(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refreshProfile()
  }, [refreshProfile])

  const login = async (email: string, password: string) => {
    const tokenRes = await authApi.login(email, password)
    tokenStorage.set(tokenRes.access_token)
    setToken(tokenRes.access_token)
    const profile = await userApi.getMe()
    setUser(profile)
  }

  const registerAndLogin = async (payload: UserRegister) => {
    await authApi.register(payload)
    await login(payload.email, payload.password)
  }

  const logout = () => {
    tokenStorage.clear()
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        registerAndLogin,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}
