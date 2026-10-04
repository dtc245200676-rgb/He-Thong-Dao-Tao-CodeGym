import { Alert, Button, Card, Form, Input, Typography } from 'antd'
import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, apiErrorMessage } from '../api/client'

export default function ActivatePage() {
  const [params] = useSearchParams()
  const token = params.get('token') || ''
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')

  const submit = async (values: { temporary_password: string }) => {
    setError('')
    try {
      await api.post('/api/auth/activate', { token, temporary_password: values.temporary_password })
      setDone(true)
    } catch (err) { setError(apiErrorMessage(err)) }
  }

  return <div className="auth-page"><Card className="auth-card">
    <Typography.Title level={2}>Kích hoạt tài khoản</Typography.Title>
    {done ? <Alert type="success" showIcon message="Kích hoạt thành công." description={<Link to="/login">Đăng nhập bằng mật khẩu tạm</Link>} /> : <>
      {error && <Alert type="error" showIcon message={error} style={{ marginBottom: 16 }} />}
      <Form layout="vertical" onFinish={submit} size="large">
        <Form.Item name="temporary_password" label="Mật khẩu tạm" rules={[{ required: true }]}><Input.Password /></Form.Item>
        <Button type="primary" htmlType="submit" disabled={!token} block>Kích hoạt</Button>
      </Form>
    </>}
  </Card></div>
}
