import { useEffect, useState } from 'react'
import { Alert, Card, Col, Row, Spin, Statistic, Typography, Tag, List } from 'antd'
import { BookOutlined, TeamOutlined, ReadOutlined, UserOutlined, ArrowUpOutlined } from '@ant-design/icons'
import { useAuth } from '../context/AuthContext'
import { api, getErrorMessage } from '../lib/api'
import { Link } from 'react-router-dom'

type Counts = { courses: number; students: number; teachers: number; enrollments: number }
export default function DashboardPage() {
  const { user } = useAuth()
  const role = user?.profile?.type
  const [counts, setCounts] = useState<Counts>({ courses: 0, students: 0, teachers: 0, enrollments: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const paths = role === 'student'
      ? [['courses', '/courses/active/'], ['enrollments', '/enrollments/']]
      : role === 'teacher'
        ? [['courses', '/courses/'], ['students', '/students/'], ['enrollments', '/enrollments/']]
        : [['courses', '/courses/'], ['students', '/students/'], ['teachers', '/teachers/'], ['enrollments', '/enrollments/']]
    Promise.all(paths.map(async ([key, path]) => {
      const { data } = await api.get(path)
      return [key, Number(data.count ?? (Array.isArray(data) ? data.length : data.results?.length ?? 0))] as const
    })).then((entries) => setCounts((old) => ({ ...old, ...Object.fromEntries(entries) })))
      .catch((e: unknown) => setError(getErrorMessage(e)))
      .finally(() => setLoading(false))
  }, [role])

  const cards = role === 'student'
    ? [{ title: '开放课程', value: counts.courses, icon: <BookOutlined />, color: 'blue' }, { title: '我的选课', value: counts.enrollments, icon: <ReadOutlined />, color: 'purple' }]
    : role === 'teacher'
      ? [{ title: '我的课程', value: counts.courses, icon: <BookOutlined />, color: 'blue' }, { title: '学生人数', value: counts.students, icon: <TeamOutlined />, color: 'green' }, { title: '选课记录', value: counts.enrollments, icon: <ReadOutlined />, color: 'purple' }]
      : [{ title: '课程总数', value: counts.courses, icon: <BookOutlined />, color: 'blue' }, { title: '学生总数', value: counts.students, icon: <TeamOutlined />, color: 'green' }, { title: '教师总数', value: counts.teachers, icon: <UserOutlined />, color: 'orange' }, { title: '选课记录', value: counts.enrollments, icon: <ReadOutlined />, color: 'purple' }]

  return <>
    <div className="page-heading"><div><Typography.Title level={2}>工作台</Typography.Title><Typography.Paragraph>欢迎回来，{user?.profile?.name || user?.username}。这里是你的课程管理概览。</Typography.Paragraph></div><Tag color={role === 'admin' ? 'gold' : role === 'teacher' ? 'blue' : 'green'}>{role === 'admin' ? '系统管理员' : role === 'teacher' ? '教师' : '学生'}</Tag></div>
    {error && <Alert type="warning" showIcon message={error} className="mb-16" />}
    <Spin spinning={loading}>
      <Row gutter={[16, 16]}>
        {cards.map((item) => <Col xs={24} sm={12} xl={role === 'admin' ? 6 : 8} key={item.title}><Card className="stat-card" bordered={false}><div className={`stat-icon ${item.color}`}>{item.icon}</div><Statistic title={item.title} value={item.value} /></Card></Col>)}
      </Row>
    </Spin>
    <Row gutter={[16, 16]} className="dashboard-lower">
      <Col xs={24} xl={15}><Card title="快速入口" bordered={false} className="panel-card"><div className="quick-links">
        <Link to="/courses" className="quick-link"><span className="quick-icon blue"><BookOutlined /></span><span><strong>课程中心</strong><small>浏览课程、管理课程信息</small></span><ArrowUpOutlined /></Link>
        <Link to="/enrollments" className="quick-link"><span className="quick-icon purple"><ReadOutlined /></span><span><strong>{role === 'student' ? '我的选课' : '选课记录'}</strong><small>查看课程选修情况</small></span><ArrowUpOutlined /></Link>
        {role !== 'student' && <Link to="/students" className="quick-link"><span className="quick-icon green"><TeamOutlined /></span><span><strong>学生管理</strong><small>查看学生资料</small></span><ArrowUpOutlined /></Link>}
      </div></Card></Col>
      <Col xs={24} xl={9}><Card title="账号信息" bordered={false} className="panel-card"><List size="small" dataSource={[['用户名', user?.username], ['邮箱', user?.email || '未填写'], ['角色', role === 'admin' ? '管理员' : role === 'teacher' ? '教师' : '学生']]} renderItem={(item) => <List.Item><span className="muted">{item[0]}</span><strong>{item[1]}</strong></List.Item>} /></Card></Col>
    </Row>
  </>
}
