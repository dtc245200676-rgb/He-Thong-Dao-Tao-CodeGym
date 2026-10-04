from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RoleBrief(BaseModel):
    id: int
    slug: str
    name: str


class UserBrief(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    status: str
    is_active: bool
    must_change_password: bool
    needs_handover: bool
    roles: list[RoleBrief]
    created_at: datetime


class UserListResponse(BaseModel):
    items: list[UserBrief]
    page: int
    page_size: int
    total: int


class UserCreateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    role_slugs: list[str] = Field(default_factory=list)


class UserCreateResponse(UserBrief):
    email_sent: bool
    debug_temporary_password: Optional[str] = None
    debug_activation_token: Optional[str] = None


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)


class AssignRolesRequest(BaseModel):
    role_slugs: list[str]


class LockAccountRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)


class UnlockAccountRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)


class PermissionBrief(BaseModel):
    id: int
    code: str
    name: str


class RoleDetail(BaseModel):
    id: int
    slug: str
    name: str
    description: Optional[str] = None
    permissions: list[PermissionBrief]


class RolePermissionsUpdate(BaseModel):
    permission_codes: list[str]
