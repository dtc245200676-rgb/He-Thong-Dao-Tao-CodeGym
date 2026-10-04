import { LockOutlined, MailOutlined } from '@ant-design/icons'
import { Alert, Button, Card, Form, Input, Typography, message } from 'antd'
import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { apiErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'

export default function LoginPage() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const notice = (location.state as { notice?: string } | null)?.notice || sessionStorage.getItem('auth_notice')

  useEffect(() => {
    if (user) navigate(user.roles.includes('system_admin') ? '/admin/users' : '/dashboard', { replace: true })
  }, [user, navigate])

  useEffect(() => () => sessionStorage.removeItem('auth_notice'), [])

  const onFinish = async (values: { email: string; password: string }) => {
    setSubmitting(true)
    setError('')
    try {
      const result = await login(values.email, values.password)
      message.success(result.message || 'Đăng nhập thành công')
      if (result.must_change_password) navigate('/change-password', { replace: true })
      else navigate(result.roles.includes('system_admin') ? '/admin/users' : '/dashboard', { replace: true })
    } catch (err) {
      setError(apiErrorMessage(err, 'Không thể đăng nhập.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <Card className="auth-card">
        <div className="auth-heading">
          <div className="brand-mark large">CG</div>
          <Typography.Title level={2}>Đăng nhập</Typography.Title>
          <Typography.Text type="secondary">Hệ thống đào tạo CodeGym</Typography.Text>
        </div>
        {notice && <Alert type="info" showIcon message={notice} style={{ marginBottom: 16 }} />}
        {error && <Alert type="error" showIcon message={error} style={{ marginBottom: 16 }} />}
        <Form layout="vertical" onFinish={onFinish} size="large">
          <Form.Item name="email" label="Email" rules={[{ required: true, message: 'Vui lòng nhập email' }, { type: 'email', message: 'Email không hợp lệ' }]}>
            <Input prefix={<MailOutlined />} placeholder="name@example.com" autoComplete="email" />
          </Form.Item>
          <Form.Item name="password" label="Mật khẩu" rules={[{ required: true, message: 'Vui lòng nhập mật khẩu' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Mật khẩu" autoComplete="current-password" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={submitting} block>Đăng nhập</Button>
        </Form>
        <div className="auth-footer"><Link to="/forgot-password">Quên mật khẩu?</Link></div>
      </Card>
    </div>
  )
}
