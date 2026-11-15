import { useCallback, useEffect, useState } from 'react'
import { Alert, Button, Card, Popconfirm, Table, Tag, Typography, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { ReloadOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { api, fetchPage, getErrorMessage, type PageResult } from '../lib/api'
import { useAuth } from '../context/AuthContext'

interface Enrollment { id: number; student: { id: number; name: string; student_no: string; user: number }; course: { id: number; title: string; capacity: number; teacher: number }; enrolled_at: string }
export default function EnrollmentsPage() {
  const { user } = useAuth()
  const role = user?.profile?.type
  const [page, setPage] = useState(1)
  const [data, setData] = useState<PageResult<Enrollment>>({ results: [], count: 0, next: null, previous: null })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const load = useCallback(async () => {
    setLoading(true); setError('')
    try { setData(await fetchPage<Enrollment>('/enrollments/', { page })) }
    catch (e) { setError(getErrorMessage(e)) }
    finally { setLoading(false) }
  }, [page])
  useEffect(() => { void load() }, [load])
  const withdraw = async (id: number) => {
    try { await api.delete(`/enrollments/${id}/`); message.success(role === 'admin' ? '选课记录已删除' : '退课成功'); await load() }
    catch (e) { message.error(getErrorMessage(e)) }
  }
  const columns: ColumnsType<Enrollment> = [
    ...(role !== 'student' ? [{ title: '学生', dataIndex: ['student', 'name'], render: (_: unknown, r: Enrollment) => <div><strong>{r.student.name}</strong><div className="muted">{r.student.student_no}</div></div> }] : []),
    { title: '课程', dataIndex: ['course', 'title'], render: (_: unknown, r: Enrollment) => <strong>{r.course.title}</strong> },
    { title: '课程 ID', dataIndex: ['course', 'id'], width: 100 },
    { title: '选课时间', dataIndex: 'enrolled_at', render: (v: string) => dayjs(v).format('YYYY-MM-DD HH:mm') },
    { title: '状态', key: 'status', render: () => <Tag color="success">已选修</Tag> },
    ...(role === 'student' || role === 'admin' ? [{ title: '操作', key: 'action', render: (_: unknown, r: Enrollment) => <Popconfirm title={role === 'student' ? '确认退选这门课程？' : '确认删除这条选课记录？'} onConfirm={() => withdraw(r.id)}><Button type="link" danger>{role === 'student' ? '退课' : '删除记录'}</Button></Popconfirm> }] : []),
  ]
  return <>
    <div className="page-heading"><div><Typography.Title level={2}>{role === 'student' ? '我的选课' : role === 'teacher' ? '学生选课记录' : '选课记录'}</Typography.Title><Typography.Paragraph>{role === 'student' ? '查看已选课程，需要时可以办理退课。' : '查看当前账号权限范围内的课程选修情况。'}</Typography.Paragraph></div><Button icon={<ReloadOutlined />} onClick={() => void load()}>刷新</Button></div>
    {error && <Alert type="error" showIcon message={error} className="mb-16" />}
    <Card bordered={false} className="table-card"><Table rowKey="id" columns={columns} dataSource={data.results} loading={loading} scroll={{ x: 650 }} pagination={{ current: page, pageSize: 10, total: data.count, showSizeChanger: false, onChange: setPage, showTotal: (total) => `共 ${total} 条选课记录` }} /></Card>
  </>
}
