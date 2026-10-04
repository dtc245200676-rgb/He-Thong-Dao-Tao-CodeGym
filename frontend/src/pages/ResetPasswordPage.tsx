import { Alert, Button, Card, Form, Input, Typography } from 'antd'
import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, apiErrorMessage } from '../api/client'

export default function ResetPasswordPage() {
  const [params] = useSearchParams()
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')
  const token = params.get('token') || ''

  const submit = async (values: { new_password: string; confirm: string }) => {
    setError('')
    if (values.new_password !== values.confirm) return setError('Xác nhận mật khẩu không khớp.')
    try {
      await api.post('/api/auth/reset-password', { token, new_password: values.new_password })
      setDone(true)
    } catch (err) { setError(apiErrorMessage(err)) }
  }

  return <div className="auth-page"><Card className="auth-card">
    <Typography.Title level={2}>Đặt lại mật khẩu</Typography.Title>
    {done ? <Alert type="success" showIcon message="Đặt lại mật khẩu thành công." description={<Link to="/login">Đăng nhập ngay</Link>} /> : <>
      {error && <Alert type="error" showIcon message={error} style={{ marginBottom: 16 }} />}
      {!token && <Alert type="warning" showIcon message="Thiếu token đặt lại mật khẩu." style={{ marginBottom: 16 }} />}
      <Form layout="vertical" onFinish={submit} size="large">
        <Form.Item name="new_password" label="Mật khẩu mới" rules={[{ required: true }, { min: 8, message: 'Tối thiểu 8 ký tự' }, { pattern: /^(?=.*[A-Za-z])(?=.*\d).+$/, message: 'Phải có cả chữ và số' }]}><Input.Password /></Form.Item>
        <Form.Item name="confirm" label="Nhập lại mật khẩu" rules={[{ required: true }]}><Input.Password /></Form.Item>
        <Button type="primary" htmlType="submit" disabled={!token} block>Đặt lại mật khẩu</Button>
      </Form>
    </>}
  </Card></div>
}
