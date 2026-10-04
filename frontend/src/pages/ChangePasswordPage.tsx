import { Alert, Button, Card, Form, Input, Typography, message } from 'antd'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'

const DRAFT_KEY = 'draft:change-password'

export default function ChangePasswordPage() {
  const { refreshMe } = useAuth()
  const [form] = Form.useForm()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const draft = sessionStorage.getItem(DRAFT_KEY)
    if (draft) {
      try { form.setFieldsValue(JSON.parse(draft)) } catch { /* ignore */ }
    }
  }, [form])

  const submit = async (values: { current_password: string; new_password: string; confirm: string }) => {
    setError('')
    if (values.new_password !== values.confirm) return setError('Xác nhận mật khẩu không khớp.')
    setLoading(true)
    try {
      await api.post('/api/auth/change-password', { current_password: values.current_password, new_password: values.new_password })
      sessionStorage.removeItem(DRAFT_KEY)
      form.resetFields()
      await refreshMe()
      message.success('Đổi mật khẩu thành công. Các phiên đăng nhập khác đã bị thu hồi.')
    } catch (err) { setError(apiErrorMessage(err)) }
    finally { setLoading(false) }
  }

  return <div className="page-wrap"><Card className="narrow-card">
    <Typography.Title level={2}>Đổi mật khẩu</Typography.Title>
    <Typography.Paragraph type="secondary">Mật khẩu mới tối thiểu 8 ký tự và phải có cả chữ lẫn số.</Typography.Paragraph>
    {error && <Alert type="error" showIcon message={error} style={{ marginBottom: 16 }} />}
    <Form form={form} layout="vertical" onFinish={submit} onValuesChange={(_, all) => sessionStorage.setItem(DRAFT_KEY, JSON.stringify({ current_password: all.current_password || '', new_password: all.new_password || '', confirm: all.confirm || '' }))}>
      <Form.Item name="current_password" label="Mật khẩu hiện tại" rules={[{ required: true }]}><Input.Password /></Form.Item>
      <Form.Item name="new_password" label="Mật khẩu mới" rules={[{ required: true }, { min: 8 }, { pattern: /^(?=.*[A-Za-z])(?=.*\d).+$/, message: 'Mật khẩu phải có cả chữ và số' }]}><Input.Password /></Form.Item>
      <Form.Item name="confirm" label="Nhập lại mật khẩu mới" rules={[{ required: true }]}><Input.Password /></Form.Item>
      <Button type="primary" htmlType="submit" loading={loading}>Đổi mật khẩu</Button>
    </Form>
  </Card></div>
}
