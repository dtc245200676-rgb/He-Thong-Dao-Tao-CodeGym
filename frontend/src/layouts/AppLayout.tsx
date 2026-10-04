import {
  DashboardOutlined,
  KeyOutlined,
  LogoutOutlined,
  MenuOutlined,
  SafetyCertificateOutlined,
  TeamOutlined,
} from '@ant-design/icons'
import { Avatar, Button, Drawer, Grid, Layout, Menu, Space, Tag, Typography } from 'antd'
import { useMemo, useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const { Header, Sider, Content } = Layout

const roleLabels: Record<string, string> = {
  system_admin: 'Quản trị hệ thống',
  training_manager: 'Quản lý đào tạo',
  teacher: 'Giảng viên',
  accountant: 'Kế toán',
  academic_affairs: 'Giáo vụ',
  admissions: 'Tuyển sinh',
  student_services: 'Công tác sinh viên',
  student: 'Học viên',
}

export default function AppLayout() {
  const { user, logout, hasPermission } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const screens = Grid.useBreakpoint()
  const mobile = !screens.md
  const [drawerOpen, setDrawerOpen] = useState(false)

  const items = useMemo(() => [
    hasPermission('dashboard.view') ? { key: '/dashboard', icon: <DashboardOutlined />, label: 'Tổng quan' } : null,
    hasPermission('users.view') ? { key: '/admin/users', icon: <TeamOutlined />, label: 'Người dùng' } : null,
    hasPermission('roles.view') ? { key: '/admin/roles', icon: <SafetyCertificateOutlined />, label: 'Vai trò & quyền' } : null,
    { key: '/change-password', icon: <KeyOutlined />, label: 'Đổi mật khẩu' },
  ].filter(Boolean) as { key: string; icon: React.ReactNode; label: string }[], [hasPermission])

  const menu = (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname]}
      items={items}
      onClick={({ key }) => {
        navigate(key)
        setDrawerOpen(false)
      }}
    />
  )

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true, state: { notice: 'Bạn đã đăng xuất an toàn.' } })
  }

  return (
    <Layout className="app-shell">
      {!mobile && (
        <Sider width={240} theme="light" className="app-sider">
          <div className="brand-block">
            <div className="brand-mark">CG</div>
            <div><strong>CodeGym</strong><small>Hệ thống đào tạo</small></div>
          </div>
          {menu}
        </Sider>
      )}
      <Drawer title="Điều hướng" placement="left" width={300} open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        {menu}
      </Drawer>
      <Layout>
        <Header className="app-header">
          <Space>
            {mobile && <Button type="text" icon={<MenuOutlined />} onClick={() => setDrawerOpen(true)} />}
            <Typography.Text strong>Hệ thống quản lý đào tạo</Typography.Text>
          </Space>
          <Space wrap>
            <Avatar>{(user?.full_name || user?.email || 'U').charAt(0).toUpperCase()}</Avatar>
            <div className="header-user">
              <strong>{user?.full_name || user?.email}</strong>
              <Space size={4} wrap>
                {user?.roles.map((role) => <Tag key={role}>{roleLabels[role] || role}</Tag>)}
              </Space>
            </div>
            <Button icon={<LogoutOutlined />} onClick={handleLogout}>Đăng xuất</Button>
          </Space>
        </Header>
        <Content className="app-content"><Outlet /></Content>
      </Layout>
    </Layout>
  )
}
