import { useCallback, useEffect, useState } from 'react'
import {
  Alert, Button, Card, Descriptions, Form, Input, InputNumber, Modal, Popconfirm,
  Select, Space, Switch, Table, Tag, Typography, message,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import {
  BookOutlined, PlusOutlined, ReloadOutlined, SearchOutlined, EyeOutlined,
} from '@ant-design/icons'
import { api, fetchPage, getErrorMessage, type PageResult } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import dayjs from 'dayjs'

interface Course {
  id: number
  teacher: number
  code: string
  enrollment_count: number
  title: string
  description: string
  capacity: number
  is_active: boolean
  created_at: string
  updated_at: string
}

interface Teacher {
  id: number
  user?: number
  name: string
  department: string
}

interface Enrollment {
  id: number
  course: {
    id: number
    title: string
  }
}

export default function CoursesPage() {
  const { user } = useAuth()
  const role = user?.profile?.type
  const canManage = role === 'admin' || role === 'teacher'

  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [data, setData] = useState<PageResult<Course>>({
    results: [], count: 0, next: null, previous: null,
  })
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [enrolledCourseIds, setEnrolledCourseIds] = useState<Set<number>>(new Set())
  const [enrollmentsLoading, setEnrollmentsLoading] = useState(false)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Course | null>(null)
  const [detail, setDetail] = useState<Course | null>(null)
  const [form] = Form.useForm()

  const load = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const endpoint = role === 'student' ? '/courses/active/' : '/courses/'
      const result = await fetchPage<Course>(endpoint, {
        page,
        search: search || undefined,
      })
      setData(result)
    } catch (e) {
      setError(getErrorMessage(e))
    } finally {
      setLoading(false)
    }
  }, [page, role, search])

  // 获取当前学生的全部选课记录，而不只是第一页
  const loadEnrollments = useCallback(async () => {
    if (role !== 'student') return

    setEnrollmentsLoading(true)

    try {
      const allEnrollments: Enrollment[] = []
      let currentPage = 1

      while (true) {
        const { data } = await api.get('/enrollments/', {
          params: {
            page: currentPage,
            page_size: 50,
          },
        })

        const results: Enrollment[] = Array.isArray(data)
          ? data
          : (data.results ?? [])

        allEnrollments.push(...results)

        if (Array.isArray(data) || !data.next || results.length === 0) {
          break
        }

        currentPage += 1
      }

      setEnrolledCourseIds(
        new Set(allEnrollments.map((item) => item.course.id)),
      )
    } catch (e) {
      message.error(`加载已选课程失败：${getErrorMessage(e)}`)
    } finally {
      setEnrollmentsLoading(false)
    }
  }, [role])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    if (role === 'student') {
      void loadEnrollments()
    } else {
      setEnrolledCourseIds(new Set())
    }
  }, [role, loadEnrollments])

  useEffect(() => {
    api.get('/teachers/', { params: { page_size: 100 } })
      .then(({ data }) => setTeachers(data.results ?? data))
      .catch(() => setTeachers([]))
  }, [])

  const openForm = (record?: Course) => {
    setEditing(record ?? null)
    form.setFieldsValue(
      record ? { ...record } : { capacity: 30, is_active: true },
    )
    setOpen(true)
  }

  const save = async (values: Record<string, unknown>) => {
    try {
      if (editing) {
        await api.patch(`/courses/${editing.id}/`, values)
      } else {
        await api.post('/courses/', values)
      }

      message.success(editing ? '课程已更新' : '课程创建成功')
      setOpen(false)
      await load()
    } catch (e) {
      message.error(getErrorMessage(e))
    }
  }

  const showDetail = async (id: number) => {
    try {
      const { data: course } = await api.get<Course>(`/courses/${id}/`)
      setDetail(course)
    } catch (e) { message.error(getErrorMessage(e)) }
  }

  const remove = async (id: number) => {
    try {
      await api.delete(`/courses/${id}/`)
      message.success('课程已删除')
      await load()
    } catch (e) {
      message.error(getErrorMessage(e))
    }
  }

  const enroll = async (id: number) => {
    try {
      await api.post('/enrollments/', { course_id: id })

      // 选课成功后立即更新本地状态
      setEnrolledCourseIds((previous) => {
        const next = new Set(previous)
        next.add(id)
        return next
      })

      message.success('选课成功')
    } catch (e) {
      message.error(getErrorMessage(e))

      // 如果请求失败，也重新同步一次选课记录
      await loadEnrollments()
    }
  }

  const columns: ColumnsType<Course> = [
    {
      title: '课程名称',
      dataIndex: 'title',
      render: (v: string, r) => (
        <div className="course-cell">
          <span className="course-symbol"><BookOutlined /></span>
          <span>
            <strong>{v}</strong>
            <small>{r.code || `课程 ID #${r.id}`}</small>
          </span>
        </div>
      ),
    },
    {
      title: '课程介绍',
      dataIndex: 'description',
      ellipsis: true,
      responsive: ['lg'],
    },
    {
      title: '授课教师',
      dataIndex: 'teacher',
      render: (v: number) =>
        teachers.find((t) => t.id === v)?.name ?? `教师 #${v}`,
    },
    {
      title: '选课人数',
      dataIndex: 'enrollment_count',
      width: 105,
      render: (value: number, record) => `${value ?? 0} / ${record.capacity} 人`,
    },
    {
      title: '容量',
      dataIndex: 'capacity',
      width: 90,
      render: (v: number) => `${v} 人`,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      width: 100,
      render: (v: boolean) => (
        <Tag color={v ? 'success' : 'default'}>
          {v ? '开放选课' : '已关闭'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      responsive: ['xl'],
      render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 240,
      render: (_, record) => (
        <Space size="small">
          <Button type="link" icon={<EyeOutlined />} onClick={() => void showDetail(record.id)}>详情</Button>
          {role === 'student' && (
            enrolledCourseIds.has(record.id)
              ? <Tag color="success">已选</Tag>
              : (
                <Popconfirm
                  title="确认选择这门课程？"
                  onConfirm={() => enroll(record.id)}
                >
                  <Button
                    type="link"
                    disabled={!record.is_active || enrollmentsLoading}
                  >
                    选课
                  </Button>
                </Popconfirm>
              )
          )}

          {(role === 'admin' || (
            role === 'teacher' &&
            record.teacher === teachers.find(
              (t) => t.user === user?.id,
            )?.id
          )) && (
            <Button type="link" onClick={() => openForm(record)}>
              编辑
            </Button>
          )}

          {role === 'admin' && (
            <Popconfirm
              title="确定删除该课程？"
              description="已有学生选课的课程无法删除。"
              onConfirm={() => remove(record.id)}
            >
              <Button type="link" danger>删除</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <>
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>课程中心</Typography.Title>
          <Typography.Paragraph>
            {role === 'student'
              ? '浏览当前开放课程，选择你感兴趣的课程。'
              : '查看课程信息，并根据权限维护课程。'}
          </Typography.Paragraph>
        </div>

        {canManage && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => openForm()}
          >
            新建课程
          </Button>
        )}
      </div>

      {error && (
        <Alert
          type="error"
          showIcon
          message={error}
          className="mb-16"
        />
      )}

      <Card bordered={false} className="table-card">
        <div className="table-toolbar">
          <Input
            allowClear
            prefix={<SearchOutlined />}
            placeholder="搜索课程名称或介绍"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            onPressEnter={() => void load()}
            style={{ maxWidth: 320 }}
          />

          <Button
            icon={<ReloadOutlined />}
            onClick={() => {
              void load()
              if (role === 'student') void loadEnrollments()
            }}
          >
            刷新
          </Button>
        </div>

        <Table
          rowKey="id"
          columns={columns}
          dataSource={data.results}
          loading={loading || (role === 'student' && enrollmentsLoading)}
          scroll={{ x: 850 }}
          pagination={{
            current: page,
            pageSize: 10,
            total: data.count,
            showSizeChanger: false,
            onChange: setPage,
            showTotal: (total) => `共 ${total} 门课程`,
          }}
        />
      </Card>

      <Modal
        title={editing ? '编辑课程' : '新建课程'}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
        okText="保存"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={save}>
          <Form.Item
            name="title"
            label="课程名称"
            rules={[
              { required: true, whitespace: true, message: '请输入课程名称' },
            ]}
          >
            <Input maxLength={100} />
          </Form.Item>

          <Form.Item name="description" label="课程介绍">
            <Input.TextArea rows={3} />
          </Form.Item>

          <Form.Item
            name="capacity"
            label="课程容量"
            rules={[
              { required: true, type: 'number', min: 1, message: '容量至少为 1' },
            ]}
          >
            <InputNumber min={1} max={10000} style={{ width: '100%' }} />
          </Form.Item>

          {role === 'admin' && !editing && (
            <Form.Item
              name="teacher_id"
              label="授课教师 ID"
              rules={[{ required: true, message: '请输入教师资料 ID' }]}
            >
              <Select
                showSearch
                optionFilterProp="label"
                options={teachers.map((t) => ({
                  value: t.id,
                  label: `${t.name}（ID: ${t.id}）`,
                }))}
                placeholder="选择教师"
              />
            </Form.Item>
          )}

          {editing && (
            <Form.Item
              name="is_active"
              label="开放选课"
              valuePropName="checked"
            >
              <Switch checkedChildren="开放" unCheckedChildren="关闭" />
            </Form.Item>
          )}
        </Form>
      </Modal>

      <Modal title="课程详情" open={!!detail} onCancel={() => setDetail(null)} footer={<Button onClick={() => setDetail(null)}>关闭</Button>}>
        {detail && <Descriptions bordered column={1}>
          <Descriptions.Item label="课程编号">{detail.code}</Descriptions.Item>
          <Descriptions.Item label="课程 ID">{detail.id}</Descriptions.Item>
          <Descriptions.Item label="课程名称">{detail.title}</Descriptions.Item>
          <Descriptions.Item label="课程介绍">{detail.description || '暂无介绍'}</Descriptions.Item>
          <Descriptions.Item label="授课教师">{teachers.find((t) => t.id === detail.teacher)?.name ?? `教师 #${detail.teacher}`}</Descriptions.Item>
          <Descriptions.Item label="选课人数">{detail.enrollment_count ?? 0} / {detail.capacity}</Descriptions.Item>
          <Descriptions.Item label="状态"><Tag color={detail.is_active ? 'success' : 'default'}>{detail.is_active ? '开放选课' : '已关闭'}</Tag></Descriptions.Item>
          <Descriptions.Item label="创建时间">{detail.created_at ? dayjs(detail.created_at).format('YYYY-MM-DD HH:mm') : '-'}</Descriptions.Item>
        </Descriptions>}
      </Modal>
    </>
  )
}
