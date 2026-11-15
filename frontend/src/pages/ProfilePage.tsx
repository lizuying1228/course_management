import { Card, Descriptions, Typography, Tag } from 'antd'
import { useAuth } from '../context/AuthContext'
export default function ProfilePage() {
  const { user } = useAuth()
  const profile = user?.profile
  const role = profile?.type
  return <>
    <div className="page-heading"><div><Typography.Title level={2}>个人资料</Typography.Title><Typography.Paragraph>当前登录账号的基本信息。</Typography.Paragraph></div></div>
    <Card bordered={false} className="profile-card"><Descriptions column={{ xs: 1, sm: 2 }} bordered>
      <Descriptions.Item label="用户 ID">{user?.id}</Descriptions.Item>
      <Descriptions.Item label="用户名">{user?.username}</Descriptions.Item>
      <Descriptions.Item label="邮箱">{user?.email || '未填写'}</Descriptions.Item>
      <Descriptions.Item label="角色"><Tag color={role === 'admin' ? 'gold' : role === 'teacher' ? 'blue' : 'green'}>{role === 'admin' ? '管理员' : role === 'teacher' ? '教师' : '学生'}</Tag></Descriptions.Item>
      {profile?.name && <Descriptions.Item label="姓名">{profile.name}</Descriptions.Item>}
      {profile?.student_no && <Descriptions.Item label="学号">{profile.student_no}</Descriptions.Item>}
      {profile?.age && <Descriptions.Item label="年龄">{profile.age}</Descriptions.Item>}
      {profile?.department && <Descriptions.Item label="所属院系">{profile.department}</Descriptions.Item>}
    </Descriptions></Card>
  </>
}
