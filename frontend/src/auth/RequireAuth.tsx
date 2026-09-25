import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { LoadingPage } from '../components/PageState'
import { useAuth } from './AuthContext'

export function RequireAuth() {
  const { user, ready } = useAuth()
  const location = useLocation()
  if (!ready) return <LoadingPage text="Đang kiểm tra đăng nhập..." />
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return <Outlet />
}
