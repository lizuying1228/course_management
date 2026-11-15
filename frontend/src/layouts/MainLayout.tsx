import { useMemo, useState } from 'react'
import { Layout, Menu, Avatar, Dropdown, Button } from 'antd'
import type { MenuProps } from 'antd'
import {
  AppstoreOutlined, BookOutlined, TeamOutlined, UserOutlined, ReadOutlined,
  LogoutOutlined, MenuFoldOutlined, MenuUnfoldOutlined, SafetyCertificateOutlined,
} from '@ant-design/icons'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const { Sider, Header, Content } = Layout
const roleName = { admin: '系统管理员', teacher: '教师', student: '学生' }

export default function MainLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  const role = user?.profile?.type ?? 'student'

  const items = useMemo(() => {
    const base: MenuProps['items'] = [
      { key: '/', icon: <AppstoreOutlined />, label: '工作台' },
      { key: '/courses', icon: <BookOutlined />, label: '课程中心' },
      { key: '/enrollments', icon: <ReadOutlined />, label: role === 'student' ? '我的选课' : role === 'teacher' ? '学生选课' : '选课记录' },
    ]
    if (role === 'admin' || role === 'teacher') base.push({ key: '/students', icon: <TeamOutlined />, label: '学生管理' })
    if (role !== 'student') base.push({ key: '/teachers', icon: <UserOutlined />, label: '教师管理' })
    if (role === 'admin') base.push({ key: '/system', icon: <SafetyCertificateOutlined />, label: '系统信息' })
    return base
  }, [role])

  const menu = (
    <Menu
      selectedKeys={[location.pathname]}
      items={items}
      onClick={({ key }) => navigate(key)}
      className="side-menu"
    />
  )
  const profileItems: MenuProps['items'] = [
    { key: 'profile', icon: <UserOutlined />, label: '个人资料' },
    { type: 'divider' },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true },
  ]

  return (
    <Layout className="app-shell">
      <Sider width={238} theme="light" collapsible collapsed={collapsed} trigger={null} className="app-sider">
        <div className="brand"><div className="brand-mark"><BookOutlined /></div>{!collapsed && <div><strong>CourseHub</strong><span>课程管理平台</span></div>}</div>
        {!collapsed && <div className="nav-caption">工作空间</div>}
        {menu}
        <div className="sider-bottom">{!collapsed && <><div className="sider-bottom-title">课程管理系统</div><div className="sider-bottom-sub">学习 · 教学 · 管理</div></>}</div>
      </Sider>
      <Layout>
        <Header className="app-header">
          <Button type="text" className="collapse-button" icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />} onClick={() => setCollapsed(!collapsed)} />
          <div className="header-spacer" />
          <Dropdown menu={{ items: profileItems, onClick: async ({ key }) => {
            if (key === 'profile') navigate('/profile')
            if (key === 'logout') { await logout(); navigate('/login') }
          } }} trigger={['click']}>
            <button className="user-menu">
              <Avatar style={{ background: '#e7edff', color: '#435bd5' }} icon={<UserOutlined />} />
              <span className="user-meta"><strong>{user?.profile?.name || user?.username}</strong><small>{roleName[role]}</small></span>
            </button>
          </Dropdown>
        </Header>
        <Content className="app-content"><div className="content-inner"><Outlet /></div></Content>
      </Layout>
    </Layout>
  )
}
