import { Navigate, Outlet } from 'react-router-dom'
import { Spin } from 'antd'
import { useAuth, type Role } from '../context/AuthContext'

export default function ProtectedRoute({ roles }: { roles?: Role[] }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="screen-center"><Spin size="large" /></div>
  if (!user) return <Navigate to="/login" replace />
  if (roles && (!user.profile || !roles.includes(user.profile.type))) return <Navigate to="/" replace />
  return <Outlet />
}
