from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, require_permission
from app.db.database import get_db
from app.models.role import Permission, Role
from app.schemas.user import RolePermissionsUpdate

router = APIRouter(prefix="/api/roles", tags=["Roles & Permissions"])


def serialize_role(role: Role) -> dict:
    return {
        "id": role.id,
        "slug": role.slug,
        "name": role.name,
        "description": role.description,
        "permissions": [
            {"id": permission.id, "code": permission.code, "name": permission.name}
            for permission in sorted(role.permissions, key=lambda p: p.code)
        ],
    }


@router.get("")
def list_roles(
    _: AuthContext = Depends(require_permission("roles.view")),
    db: Session = Depends(get_db),
):
    roles = db.scalars(select(Role).options(selectinload(Role.permissions)).order_by(Role.id)).all()
    permissions = db.scalars(select(Permission).order_by(Permission.code)).all()
    return {
        "roles": [serialize_role(role) for role in roles],
        "permissions": [{"id": p.id, "code": p.code, "name": p.name} for p in permissions],
    }


@router.put("/{role_id}/permissions")
def update_role_permissions(
    role_id: int,
    data: RolePermissionsUpdate,
    _: AuthContext = Depends(require_permission("roles.manage")),
    db: Session = Depends(get_db),
):
    role = db.scalar(select(Role).where(Role.id == role_id).options(selectinload(Role.permissions)))
    if not role:
        raise HTTPException(status_code=404, detail="Không tìm thấy vai trò.")
    permissions = db.scalars(select(Permission).where(Permission.code.in_(set(data.permission_codes)))).all()
    if len(permissions) != len(set(data.permission_codes)):
        raise HTTPException(status_code=400, detail="Có quyền không hợp lệ trong danh sách.")
    role.permissions = list(permissions)
    db.commit()
    db.refresh(role)
    return serialize_role(role)
