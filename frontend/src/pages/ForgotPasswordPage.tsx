import { Alert, Button, Card, Form, Input, Typography } from 'antd'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api, apiErrorMessage } from '../api/client'

export default function ForgotPasswordPage() {
  const [result, setResult] = useState<{ message: string } | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (values: { email: string }) => {
    setLoading(true); setError('')
    try {
      const response = await api.post('/api/auth/forgot-password', values)
      setResult(response.data)
    } catch (err) { setError(apiErrorMessage(err)) }
    finally { setLoading(false) }
  }

  return <div className="auth-page"><Card className="auth-card">
    <Typography.Title level={2}>Quên mật khẩu</Typography.Title>
    <Typography.Paragraph type="secondary">Nhập email. Hệ thống luôn trả cùng một thông báo để bảo vệ thông tin tài khoản.</Typography.Paragraph>
    {error && <Alert type="error" showIcon message={error} style={{ marginBottom: 16 }} />}
    {result && <Alert type="success" showIcon message={result.message} style={{ marginBottom: 16 }} />}
    <Form layout="vertical" onFinish={submit} size="large">
      <Form.Item name="email" label="Email" rules={[{ required: true }, { type: 'email' }]}><Input /></Form.Item>
      <Button type="primary" htmlType="submit" loading={loading} block>Gửi liên kết đặt lại</Button>
    </Form>
    <div className="auth-footer"><Link to="/login">Quay lại đăng nhập</Link></div>
  </Card></div>
}
