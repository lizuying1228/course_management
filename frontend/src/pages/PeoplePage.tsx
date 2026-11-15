import { useCallback, useEffect, useState } from 'react'
import {
  Alert, Button, Card, Descriptions, Form, Input, InputNumber, Modal,
  Popconfirm, Select, Space, Table, Tag, Typography, message,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import {
  PlusOutlined, ReloadOutlined, SearchOutlined, UserOutlined,
  EyeOutlined, CheckCircleOutlined,
} from '@ant-design/icons'
import { api, fetchPage, getErrorMessage, type PageResult } from '../lib/api'
import { useAuth } from '../context/AuthContext'

interface PersonBase {
  id: number
  user: number
  username: string
  account_active: boolean
  name: string
}
interface Student extends PersonBase { student_no: string; age: number }
interface Teacher extends PersonBase { department: string }
type Person = Student | Teacher

export default function PeoplePage({ kind }: { kind: 'students' | 'teachers' }) {
  const { user } = useAuth()
  const isStudentList = kind === 'students'
  const role = user?.profile?.type
  const isAdmin = role === 'admin'
  const canCreate = isAdmin
  const canEdit = isAdmin || (!isStudentList && role === 'teacher')
  const [page, setPage] = useState(1)
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [accountStatus, setAccountStatus] = useState<string | undefined>()
  const [data, setData] = useState<PageResult<Person>>({ results: [], count: 0, next: null, previous: null })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState<Person | null>(null)
  const [detail, setDetail] = useState<Person | null>(null)
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      setData(await fetchPage<Person>(`/${kind}/`, {
        page,
        search: search || undefined,
        user__is_active: accountStatus,
      }))
    } catch (e) { setError(getErrorMessage(e)) }
    finally { setLoading(false) }
  }, [kind, page, search, accountStatus])
  useEffect(() => { void load() }, [load])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ age: 18 })
    setOpen(true)
  }
  const openEdit = (record: Person) => {
    setEditing(record)
    form.resetFields()
    form.setFieldsValue(record)
    setOpen(true)
  }
  const save = async (values: Record<string, unknown>) => {
    try {
      if (editing) {
        await api.patch(`/${kind}/${editing.id}/`, values)
        message.success('资料已更新')
      } else {
        await api.post(`/${kind}/`, values)
        message.success(isStudentList ? '学生账号和资料创建成功' : '教师账号和资料创建成功')
      }
      setOpen(false)
      await load()
    } catch (e) { message.error(getErrorMessage(e)) }
  }
  const showDetail = async (record: Person) => {
    try {
      const { data: full } = await api.get<Person>(`/${kind}/${record.id}/`)
      setDetail(full)
    } catch (e) { message.error(getErrorMessage(e)) }
  }
  const remove = async (record: Person) => {
    try {
      await api.delete(`/${kind}/${record.id}/`)
      message.success(isStudentList ? '学生账号已停用，资料和选课历史已保留' : '教师资料已删除')
      await load()
    } catch (e) { message.error(getErrorMessage(e)) }
  }
  const restore = async (record: Person) => {
    try {
      await api.post(`/students/${record.id}/restore/`)
      message.success('学生账号已恢复')
      await load()
    } catch (e) { message.error(getErrorMessage(e)) }
  }

  const columns: ColumnsType<Person> = [
    {
      title: isStudentList ? '学生' : '教师', dataIndex: 'name',
      render: (value: string, record) => <div className="person-cell"><span className={`person-avatar ${isStudentList ? 'student' : 'teacher'}`}><UserOutlined /></span><span><strong>{value}</strong><small>资料 ID #{record.id} · 用户名 {record.username || `用户 #${record.user}`}</small></span></div>,
    },
    ...(isStudentList ? [
      { title: '学号', dataIndex: 'student_no' },
      { title: '年龄', dataIndex: 'age', width: 90, render: (value: number) => `${value} 岁` },
    ] as ColumnsType<Person> : [
      { title: '所属院系', dataIndex: 'department', render: (value: string) => value || '未填写' },
    ] as ColumnsType<Person>),
    { title: '账号状态', dataIndex: 'account_active', width: 110, render: (active: boolean) => <Tag color={active ? 'success' : 'default'}>{active ? '正常' : '已停用'}</Tag> },
    { title: '用户 ID', dataIndex: 'user', width: 90 },
    {
      title: '操作', key: 'action', width: 210, fixed: 'right',
      render: (_, record) => <Space size={2}>
        <Button type="link" icon={<EyeOutlined />} onClick={() => void showDetail(record)}>详情</Button>
        {canEdit && (isStudentList ? isAdmin : (isAdmin || record.user === user?.id)) && <Button type="link" onClick={() => openEdit(record)}>编辑</Button>}
        {isAdmin && isStudentList && record.account_active && <Popconfirm title="停用该学生账号？" description="学生将无法登录；资料和历史选课记录会保留。" onConfirm={() => void remove(record)}><Button type="link" danger>停用</Button></Popconfirm>}
        {isAdmin && isStudentList && !record.account_active && <Popconfirm title="恢复该学生账号？" onConfirm={() => void restore(record)}><Button type="link" icon={<CheckCircleOutlined />}>恢复</Button></Popconfirm>}
        {isAdmin && !isStudentList && <Popconfirm title="确定删除该教师资料和关联账号？" description="如果教师仍有课程，后端会阻止删除。" onConfirm={() => void remove(record)}><Button type="link" danger>删除</Button></Popconfirm>}
      </Space>,
    },
  ]

  return <>
    <div className="page-heading">
      <div><Typography.Title level={2}>{isStudentList ? '学生管理' : '教师管理'}</Typography.Title><Typography.Paragraph>{isStudentList ? '支持新增学生账号、查看详情、搜索、编辑、停用和恢复。停用不会删除学生资料及选课历史。' : '管理教师资料和账号；教师只能编辑自己的资料。'}</Typography.Paragraph></div>
      {canCreate && <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新增{isStudentList ? '学生' : '教师'}</Button>}
    </div>
    {error && <Alert type="error" showIcon message={error} className="mb-16" />}
    <Card bordered={false} className="table-card">
      <div className="table-toolbar" style={{ gap: 12, flexWrap: 'wrap' }}>
        <Space wrap>
          <Input allowClear prefix={<SearchOutlined />} placeholder={isStudentList ? '搜索姓名、学号、用户名或 ID' : '搜索姓名、院系、用户名或 ID'} value={searchInput} onChange={(e) => setSearchInput(e.target.value)} onPressEnter={() => { setPage(1); setSearch(searchInput.trim()) }} style={{ width: 300, maxWidth: '70vw' }} />
          <Button type="primary" ghost onClick={() => { setPage(1); setSearch(searchInput.trim()) }}>搜索</Button>
          <Select allowClear placeholder="账号状态" value={accountStatus} onChange={(value) => { setPage(1); setAccountStatus(value) }} style={{ width: 120 }} options={[{ value: 'true', label: '正常' }, { value: 'false', label: '已停用' }]} />
        </Space>
        <Button icon={<ReloadOutlined />} onClick={() => void load()}>刷新</Button>
      </div>
      <Table rowKey="id" columns={columns} dataSource={data.results} loading={loading} scroll={{ x: 900 }} pagination={{ current: page, pageSize: 20, total: data.count, showSizeChanger: false, onChange: setPage, showTotal: (total) => `共 ${total} 条资料` }} />
    </Card>

    <Modal title={`${editing ? '编辑' : '新增'}${isStudentList ? '学生' : '教师'}`} open={open} onCancel={() => setOpen(false)} onOk={() => form.submit()} okText="保存" cancelText="取消" destroyOnClose>
      <Form form={form} layout="vertical" onFinish={save}>
        {!editing && <>
          <Form.Item name="username" label="登录用户名" rules={[{ required: true, whitespace: true, message: '请输入用户名' }]}><Input autoComplete="off" /></Form.Item>
          <Form.Item name="password" label="初始密码" rules={[{ required: true, min: 8, message: '密码至少 8 位' }]}><Input.Password autoComplete="new-password" /></Form.Item>
          <Form.Item name="email" label="邮箱"><Input type="email" /></Form.Item>
        </>}
        <Form.Item name="name" label="姓名" rules={[{ required: true, whitespace: true, message: '请输入姓名' }]}><Input maxLength={50} /></Form.Item>
        {isStudentList ? <>
          <Form.Item name="student_no" label="学号" rules={[{ required: true, whitespace: true, message: '请输入学号' }]}><Input maxLength={50} /></Form.Item>
          <Form.Item name="age" label="年龄" rules={[{ required: true, type: 'number', min: 1, message: '请输入有效年龄' }]}><InputNumber min={1} style={{ width: '100%' }} /></Form.Item>
        </> : <Form.Item name="department" label="所属院系"><Input maxLength={100} /></Form.Item>}
      </Form>
    </Modal>

    <Modal title={`${isStudentList ? '学生' : '教师'}详情`} open={!!detail} onCancel={() => setDetail(null)} footer={<Button onClick={() => setDetail(null)}>关闭</Button>}>
      {detail && <Descriptions bordered column={1}>
        <Descriptions.Item label="资料 ID">{detail.id}</Descriptions.Item>
        <Descriptions.Item label="姓名">{detail.name}</Descriptions.Item>
        <Descriptions.Item label="用户名">{detail.username}</Descriptions.Item>
        <Descriptions.Item label="用户 ID">{detail.user}</Descriptions.Item>
        <Descriptions.Item label="账号状态"><Tag color={detail.account_active ? 'success' : 'default'}>{detail.account_active ? '正常' : '已停用'}</Tag></Descriptions.Item>
        {isStudentList && 'student_no' in detail && <Descriptions.Item label="学号">{detail.student_no}</Descriptions.Item>}
        {isStudentList && 'age' in detail && <Descriptions.Item label="年龄">{detail.age}</Descriptions.Item>}
        {!isStudentList && 'department' in detail && <Descriptions.Item label="所属院系">{detail.department || '未填写'}</Descriptions.Item>}
      </Descriptions>}
    </Modal>
  </>
}
