import { LockOutlined, PlusOutlined, UnlockOutlined, WarningOutlined } from '@ant-design/icons'
import {
  Alert,
  Button,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  Tooltip,
  Typography,
  message,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import type { RoleDetail, UserItem } from '../types'

const DRAFT_KEY = 'draft:user-management'

const statusMap: Record<string, { color: string; label: string }> = {
  active: { color: 'green', label: 'Hoạt động' },
  pending: { color: 'gold', label: 'Chờ kích hoạt' },
  locked: { color: 'red', label: 'Đã khóa' },
}

export default function UserManagementPage() {
  const { hasPermission } = useAuth()
  const [users, setUsers] = useState<UserItem[]>([])
  const [roles, setRoles] = useState<RoleDetail[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [q, setQ] = useState('')
  const [role, setRole] = useState<string>()
  const [status, setStatus] = useState<string>()
  const [loading, setLoading] = useState(false)
  const [editUser, setEditUser] = useState<UserItem | null>(null)
  const [userModalOpen, setUserModalOpen] = useState(false)
  const [lockTarget, setLockTarget] = useState<{ user: UserItem; action: 'lock' | 'unlock' } | null>(null)
  const [form] = Form.useForm()
  const [lockForm] = Form.useForm()

  const loadRoles = async () => {
    if (!hasPermission('roles.view')) return
    const response = await api.get('/api/roles')
    setRoles(response.data.roles)
  }
  const loadUsers = async () => {
    setLoading(true)
    try {
      const response = await api.get('/api/users', { params: { q: q || undefined, role, status, page, page_size: 20 } })
      setUsers(response.data.items); setTotal(response.data.total)
    } catch (err) { message.error(apiErrorMessage(err)) }
    finally { setLoading(false) }
  }

  useEffect(() => { loadRoles().catch(() => undefined) }, []) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { loadUsers() }, [page, role, status, q]) // eslint-disable-line react-hooks/exhaustive-deps

  const openCreate = () => {
    setEditUser(null); form.resetFields()
    const draft = sessionStorage.getItem(DRAFT_KEY)
    if (draft) { try { form.setFieldsValue(JSON.parse(draft)) } catch { /* ignore */ } }
    setUserModalOpen(true)
  }
  const openEdit = (user: UserItem) => {
    setEditUser(user)
    form.setFieldsValue({ full_name: user.full_name, email: user.email, phone: user.phone, role_slugs: user.roles.map((r) => r.slug) })
    setUserModalOpen(true)
  }

  const saveUser = async () => {
    try {
      const values = await form.validateFields()
      if (editUser) {
        await api.put(`/api/users/${editUser.id}`, { full_name: values.full_name, email: values.email, phone: values.phone || null })
        if (hasPermission('roles.assign')) await api.put(`/api/users/${editUser.id}/roles`, { role_slugs: values.role_slugs })
        message.success('Đã cập nhật người dùng')
      } else {
        const response = await api.post('/api/users', values)
        const dev = response.data.debug_temporary_password
          ? ` Mật khẩu tạm (dev): ${response.data.debug_temporary_password}`
          : ''
        message.success(`Đã tạo tài khoản.${dev}`, 8)
        sessionStorage.removeItem(DRAFT_KEY)
      }
      setUserModalOpen(false); await loadUsers()
    } catch (err) {
      if ((err as { errorFields?: unknown }).errorFields) return
      message.error(apiErrorMessage(err))
    }
  }

  const submitLock = async () => {
    if (!lockTarget) return
    try {
      const values = await lockForm.validateFields()
      const response = await api.post(`/api/users/${lockTarget.user.id}/${lockTarget.action}`, values)
      message.success(response.data.message)
      if (response.data.handover_warning) message.warning(response.data.handover_warning, 6)
      setLockTarget(null); lockForm.resetFields(); await loadUsers()
    } catch (err) {
      if ((err as { errorFields?: unknown }).errorFields) return
      message.error(apiErrorMessage(err))
    }
  }

  const columns = useMemo<ColumnsType<UserItem>>(() => [
    { title: 'Họ tên', dataIndex: 'full_name', render: (value, record) => <Space>{record.needs_handover && <Tooltip title="Cần bàn giao công việc/lớp phụ trách"><WarningOutlined style={{ color: '#fa8c16' }} /></Tooltip>}<strong>{value}</strong></Space> },
    { title: 'Email', dataIndex: 'email' },
    { title: 'Điện thoại', dataIndex: 'phone', responsive: ['md'] },
    { title: 'Vai trò', render: (_, record) => <Space wrap>{record.roles.map((r) => <Tag key={r.slug}>{r.name}</Tag>)}</Space> },
    { title: 'Trạng thái', dataIndex: 'status', render: (value) => <Tag color={statusMap[value]?.color}>{statusMap[value]?.label || value}</Tag> },
    { title: 'Thao tác', fixed: 'right', render: (_, record) => <Space wrap>
      {hasPermission('users.update') && <Button size="small" onClick={() => openEdit(record)}>Sửa</Button>}
      {hasPermission('users.lock') && record.status !== 'locked' && <Button danger size="small" icon={<LockOutlined />} onClick={() => setLockTarget({ user: record, action: 'lock' })}>Khóa</Button>}
      {hasPermission('users.lock') && record.status === 'locked' && <Button size="small" icon={<UnlockOutlined />} onClick={() => setLockTarget({ user: record, action: 'unlock' })}>Mở khóa</Button>}
    </Space> },
  ], [hasPermission])

  return <div className="page-wrap">
    <div className="page-title-row"><div><Typography.Title level={2}>Quản lý người dùng</Typography.Title><Typography.Text type="secondary">Tìm theo tên, email, số điện thoại; lọc theo vai trò và trạng thái.</Typography.Text></div>{hasPermission('users.create') && <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Tạo tài khoản</Button>}</div>
    <Space wrap className="toolbar">
      <Input.Search placeholder="Tên, email hoặc số điện thoại" allowClear style={{ width: 300 }} onSearch={(value) => { setQ(value); setPage(1) }} />
      <Select allowClear placeholder="Vai trò" style={{ minWidth: 180 }} options={roles.map((r) => ({ label: r.name, value: r.slug }))} onChange={(value) => { setRole(value); setPage(1) }} />
      <Select allowClear placeholder="Trạng thái" style={{ minWidth: 160 }} options={[{ value: 'active', label: 'Hoạt động' }, { value: 'pending', label: 'Chờ kích hoạt' }, { value: 'locked', label: 'Đã khóa' }]} onChange={(value) => { setStatus(value); setPage(1) }} />
      <Button onClick={loadUsers}>Làm mới</Button>
    </Space>
    {users.some((u) => u.needs_handover) && <Alert type="warning" showIcon message="Có tài khoản đã khóa cần kiểm tra bàn giao lớp/công việc." style={{ marginBottom: 16 }} />}
    <Table rowKey="id" loading={loading} columns={columns} dataSource={users} scroll={{ x: 900 }} pagination={{ current: page, pageSize: 20, total, showSizeChanger: false, onChange: setPage, showTotal: (n) => `${n} người dùng` }} />

    <Modal title={editUser ? 'Cập nhật người dùng' : 'Tạo tài khoản'} open={userModalOpen} onCancel={() => setUserModalOpen(false)} onOk={saveUser} okText="Lưu" cancelText="Hủy">
      <Form form={form} layout="vertical" onValuesChange={(_, all) => { if (!editUser) sessionStorage.setItem(DRAFT_KEY, JSON.stringify(all)) }}>
        <Form.Item name="full_name" label="Họ tên" rules={[{ required: true, message: 'Vui lòng nhập họ tên' }]}><Input /></Form.Item>
        <Form.Item name="email" label="Email" rules={[{ required: true }, { type: 'email' }]}><Input /></Form.Item>
        <Form.Item name="phone" label="Số điện thoại"><Input /></Form.Item>
        <Form.Item name="role_slugs" label="Vai trò" rules={[{ required: true, message: 'Chọn ít nhất một vai trò' }]}><Select mode="multiple" options={roles.map((r) => ({ label: r.name, value: r.slug }))} /></Form.Item>
      </Form>
    </Modal>

    <Modal title={lockTarget?.action === 'lock' ? 'Khóa tài khoản' : 'Mở khóa tài khoản'} open={Boolean(lockTarget)} onCancel={() => setLockTarget(null)} onOk={submitLock} okButtonProps={{ danger: lockTarget?.action === 'lock' }} okText="Xác nhận">
      <Typography.Paragraph>{lockTarget?.user.full_name} — {lockTarget?.user.email}</Typography.Paragraph>
      <Form form={lockForm} layout="vertical"><Form.Item name="reason" label="Lý do" rules={[{ required: true, min: 3, message: 'Bắt buộc ghi lý do' }]}><Input.TextArea rows={4} /></Form.Item></Form>
    </Modal>
  </div>
}
