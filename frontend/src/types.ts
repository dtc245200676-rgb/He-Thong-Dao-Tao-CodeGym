export interface CurrentUser {
  id: number
  full_name: string
  email: string
  phone?: string | null
  roles: string[]
  permissions: string[]
  must_change_password: boolean
}

export interface RoleBrief {
  id: number
  slug: string
  name: string
}

export interface UserItem {
  id: number
  full_name: string
  email: string
  phone?: string | null
  status: 'active' | 'pending' | 'locked' | string
  is_active: boolean
  must_change_password: boolean
  needs_handover: boolean
  roles: RoleBrief[]
  created_at: string
}

export interface PermissionItem {
  id: number
  code: string
  name: string
}

export interface RoleDetail extends RoleBrief {
  description?: string | null
  permissions: PermissionItem[]
}
