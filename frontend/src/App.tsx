import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import MainLayout from './layouts/MainLayout'
import { LoginPage, RegisterPage } from './pages/AuthPages'
import DashboardPage from './pages/DashboardPage'
import CoursesPage from './pages/CoursesPage'
import PeoplePage from './pages/PeoplePage'
import EnrollmentsPage from './pages/EnrollmentsPage'
import ProfilePage from './pages/ProfilePage'
import SystemPage from './pages/SystemPage'
import './styles.css'

export default function App() {
  return <ConfigProvider locale={zhCN} theme={{ token: { colorPrimary: '#5268df', colorBgLayout: '#f5f7fb', borderRadius: 10, fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif' }, components: { Card: { borderRadiusLG: 14 }, Button: { controlHeight: 38 }, Table: { headerBg: '#f7f8fc' } } }}>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="courses" element={<CoursesPage />} />
              <Route path="enrollments" element={<EnrollmentsPage />} />
              <Route path="students" element={<ProtectedRoute roles={['admin', 'teacher']} />}><Route index element={<PeoplePage kind="students" />} /></Route>
              <Route path="teachers" element={<ProtectedRoute roles={['admin', 'teacher']} />}><Route index element={<PeoplePage kind="teachers" />} /></Route>
              <Route path="profile" element={<ProfilePage />} />
              <Route path="system" element={<ProtectedRoute roles={['admin']} />}><Route index element={<SystemPage />} /></Route>
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </ConfigProvider>
}
