import { Button, Card, Checkbox, Col, Row, Space, Typography, message } from 'antd'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import type { PermissionItem, RoleDetail } from '../types'

export default function RoleManagementPage() {
  const { hasPermission } = useAuth()
  const [roles, setRoles] = useState<RoleDetail[]>([])
  const [permissions, setPermissions] = useState<PermissionItem[]>([])
  const [saving, setSaving] = useState<number | null>(null)

  const load = async () => {
    const response = await api.get('/api/roles')
    setRoles(response.data.roles)
    setPermissions(response.data.permissions)
  }
  useEffect(() => { load().catch((e) => message.error(apiErrorMessage(e))) }, [])

  const updateRole = (roleId: number, codes: string[]) => {
    setRoles((current) => current.map((role) => role.id === roleId ? { ...role, permissions: permissions.filter((p) => codes.includes(p.code)) } : role))
  }

  const save = async (role: RoleDetail) => {
    setSaving(role.id)
    try {
      await api.put(`/api/roles/${role.id}/permissions`, { permission_codes: role.permissions.map((p) => p.code) })
      message.success(`Đã cập nhật quyền cho ${role.name}`)
      await load()
    } catch (err) { message.error(apiErrorMessage(err)) }
    finally { setSaving(null) }
  }

  return <div className="page-wrap">
    <Typography.Title level={2}>Vai trò & phân quyền</Typography.Title>
    <Typography.Paragraph type="secondary">Quyền được kiểm tra ở backend. Mặc định chức năng không được cấp quyền sẽ bị từ chối.</Typography.Paragraph>
    <Row gutter={[16, 16]}>
      {roles.map((role) => <Col xs={24} lg={12} key={role.id}><Card title={role.name} extra={hasPermission('roles.manage') ? <Button type="primary" loading={saving === role.id} onClick={() => save(role)}>Lưu quyền</Button> : null}>
        <Typography.Paragraph type="secondary">{role.description}</Typography.Paragraph>
        <Checkbox.Group disabled={!hasPermission('roles.manage')} value={role.permissions.map((p) => p.code)} onChange={(values) => updateRole(role.id, values as string[])} style={{ width: '100%' }}>
          <Space direction="vertical" style={{ width: '100%' }}>{permissions.map((p) => <Checkbox value={p.code} key={p.code}><strong>{p.code}</strong> — {p.name}</Checkbox>)}</Space>
        </Checkbox.Group>
      </Card></Col>)}
    </Row>
  </div>
}
