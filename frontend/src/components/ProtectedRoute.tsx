import { Spin } from 'antd'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function ProtectedRoute({ permission }: { permission?: string }) {
  const { user, loading, hasPermission } = useAuth()
  const location = useLocation()

  if (loading) return <div className="page-center"><Spin size="large" /></div>
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  if (permission && !hasPermission(permission)) return <Navigate to="/403" replace />
  return <Outlet />
}
