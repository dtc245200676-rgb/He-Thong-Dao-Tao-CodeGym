import { Card, Col, Row, Space, Tag, Typography } from 'antd'
import { useAuth } from '../auth/AuthContext'

export default function DashboardPage() {
  const { user } = useAuth()
  return <div className="page-wrap">
    <Typography.Title level={2}>Tổng quan</Typography.Title>
    <Typography.Paragraph type="secondary">Chào {user?.full_name || user?.email}. Menu chỉ hiển thị những chức năng bạn có quyền sử dụng.</Typography.Paragraph>
    <Row gutter={[16, 16]}>
      <Col xs={24} md={12}><Card title="Vai trò hiện tại"><Space wrap>{user?.roles.map((r) => <Tag color="blue" key={r}>{r}</Tag>)}</Space></Card></Col>
      <Col xs={24} md={12}><Card title="Quyền được cấp"><Space wrap>{user?.permissions.map((p) => <Tag key={p}>{p}</Tag>)}</Space></Card></Col>
    </Row>
  </div>
}
