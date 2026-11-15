import { useState, type ReactNode } from 'react'
import { Alert, Button, Card, Form, Input, InputNumber, Typography, message } from 'antd'
import { BookOutlined, LockOutlined, UserOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { api, getErrorMessage } from '../lib/api'
import { useAuth } from '../context/AuthContext'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const submit = async (values: { username: string; password: string }) => {
    setBusy(true); setError('')
    try { await login(values.username, values.password); navigate('/', { replace: true }) }
    catch (e) { setError(getErrorMessage(e)) }
    finally { setBusy(false) }
  }
  return <AuthFrame title="欢迎回来" subtitle="登录课程管理平台，继续你的工作。">
    {error && <Alert type="error" showIcon message={error} className="auth-alert" />}
    <Form layout="vertical" size="large" onFinish={submit} requiredMark={false}>
      <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}><Input prefix={<UserOutlined />} placeholder="请输入用户名" autoComplete="username" /></Form.Item>
      <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }]}><Input.Password prefix={<LockOutlined />} placeholder="请输入密码" autoComplete="current-password" /></Form.Item>
      <Button type="primary" htmlType="submit" block loading={busy} className="auth-submit">登录</Button>
    </Form>
    <div className="auth-switch">还没有账号？ <Link to="/register">注册学生或教师账号</Link></div>
  </AuthFrame>
}

export function RegisterPage() {
  const navigate = useNavigate()
  const [role, setRole] = useState<'student' | 'teacher'>('student')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const submit = async (values: Record<string, string | number>) => {
    setBusy(true); setError('')
    try {
      const path = role === 'student' ? '/auth/register/student/' : '/auth/register/teacher/'
      await api.post(path, values)
      message.success('注册成功，请使用新账号登录')
      navigate('/login')
    } catch (e) { setError(getErrorMessage(e)) }
    finally { setBusy(false) }
  }
  return <AuthFrame title="创建账号" subtitle="注册后即可进入课程管理平台。">
    {error && <Alert type="error" showIcon message={error} className="auth-alert" />}
    <div className="role-switch"><button type="button" className={role === 'student' ? 'active' : ''} onClick={() => setRole('student')}>学生注册</button><button type="button" className={role === 'teacher' ? 'active' : ''} onClick={() => setRole('teacher')}>教师注册</button></div>
    <Form layout="vertical" size="large" onFinish={submit} requiredMark={false}>
      <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}><Input prefix={<UserOutlined />} /></Form.Item>
      <Form.Item name="password" label="密码" rules={[{ required: true, min: 8, message: '密码至少 8 位' }]}><Input.Password prefix={<LockOutlined />} /></Form.Item>
      <Form.Item name="email" label="邮箱"><Input type="email" /></Form.Item>
      <Form.Item name="name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}><Input /></Form.Item>
      {role === 'student' ? <>
        <Form.Item name="student_no" label="学号" rules={[{ required: true, message: '请输入学号' }]}><Input /></Form.Item>
        <Form.Item name="age" label="年龄" rules={[{ required: true, type: 'number', min: 1, message: '请输入有效年龄' }]}><InputNumber min={1} style={{ width: '100%' }} /></Form.Item>
      </> : <Form.Item name="department" label="所属院系"><Input /></Form.Item>}
      <Button type="primary" htmlType="submit" block loading={busy} className="auth-submit">注册</Button>
    </Form>
    <div className="auth-switch">已有账号？ <Link to="/login">返回登录</Link></div>
  </AuthFrame>
}

function AuthFrame({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return <div className="auth-page"><div className="auth-brand"><div className="brand-mark"><BookOutlined /></div><span>CourseHub</span></div><Card className="auth-card" bordered={false}><div className="auth-heading"><Typography.Title level={2}>{title}</Typography.Title><Typography.Paragraph>{subtitle}</Typography.Paragraph></div>{children}</Card><div className="auth-footer">课程管理平台 · Course Management System</div></div>
}
