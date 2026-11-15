import { Alert, Card, Descriptions, Typography } from 'antd'
export default function SystemPage() {
  return <>
    <div className="page-heading"><div><Typography.Title level={2}>系统信息</Typography.Title><Typography.Paragraph>课程管理平台运行信息。</Typography.Paragraph></div></div>
    <Card bordered={false}><Descriptions column={1} bordered><Descriptions.Item label="前端框架">React + TypeScript + Vite</Descriptions.Item><Descriptions.Item label="UI 组件库">Ant Design</Descriptions.Item><Descriptions.Item label="后端框架">Django REST Framework</Descriptions.Item><Descriptions.Item label="认证方式">Token Authentication</Descriptions.Item><Descriptions.Item label="API 文档"><a href="/api/docs/" target="_blank" rel="noreferrer">打开 Swagger API 文档</a></Descriptions.Item></Descriptions><Alert className="mt-16" type="info" showIcon message="角色权限由后端 API 控制。前端的菜单和页面限制仅用于界面体验，不替代后端权限验证。" /></Card>
  </>
}
