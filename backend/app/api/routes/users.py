import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, require_permission
from app.core.security import (
    ACTIVATION_TOKEN_EXPIRE_HOURS,
    generate_one_time_token,
    generate_temporary_password,
    hash_one_time_token,
    hash_password,
    utcnow,
)
from app.db.database import get_db
from app.models.audit import AccountLockAudit
from app.models.role import Role
from app.models.session import AuthSession
from app.models.tokens import ActivationToken
from app.models.user import User
from app.schemas.user import (
    AssignRolesRequest,
    LockAccountRequest,
    UnlockAccountRequest,
    UserCreateRequest,
    UserUpdateRequest,
)
from app.services.email_service import email_service

router = APIRouter(prefix="/api/users", tags=["User Management"])


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "status": user.status,
        "is_active": user.is_active,
        "must_change_password": user.must_change_password,
        "needs_handover": user.needs_handover,
        "roles": [{"id": r.id, "slug": r.slug, "name": r.name} for r in user.roles],
        "created_at": user.created_at,
    }


def load_roles(db: Session, slugs: list[str]) -> list[Role]:
    if not slugs:
        return []
    roles = db.scalars(select(Role).where(Role.slug.in_(set(slugs)))).all()
    if len(roles) != len(set(slugs)):
        raise HTTPException(status_code=400, detail="Có vai trò không tồn tại.")
    return list(roles)


@router.get("")
def list_users(
    q: str = "",
    role: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: AuthContext = Depends(require_permission("users.view")),
    db: Session = Depends(get_db),
):
    stmt = select(User).options(selectinload(User.roles))
    count_stmt = select(func.count(func.distinct(User.id)))
    if q.strip():
        pattern = f"%{q.strip()}%"
        condition = or_(User.full_name.like(pattern), User.email.like(pattern), User.phone.like(pattern))
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    if status:
        stmt = stmt.where(User.status == status)
        count_stmt = count_stmt.where(User.status == status)
    if role:
        stmt = stmt.join(User.roles).where(Role.slug == role)
        count_stmt = count_stmt.join(User.roles).where(Role.slug == role)

    total = db.scalar(count_stmt) or 0
    users = db.scalars(
        stmt.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).unique().all()
    return {"items": [serialize_user(user) for user in users], "page": page, "page_size": page_size, "total": total}


@router.post("")
def create_user(
    data: UserCreateRequest,
    _: AuthContext = Depends(require_permission("users.create")),
    db: Session = Depends(get_db),
):
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Email đã tồn tại trong hệ thống.")

    roles = load_roles(db, data.role_slugs or ["student"])
    temporary_password = generate_temporary_password()
    raw_activation_token = generate_one_time_token()
    now = utcnow()
    user = User(
        full_name=data.full_name.strip(),
        email=email,
        phone=data.phone,
        password_hash=hash_password(temporary_password),
        role=roles[0].slug if roles else "student",
        status="pending",
        is_active=False,
        must_change_password=True,
        roles=roles,
    )
    db.add(user)
    db.flush()
    db.add(
        ActivationToken(
            user_id=user.id,
            token_hash=hash_one_time_token(raw_activation_token),
            expires_at=now + timedelta(hours=ACTIVATION_TOKEN_EXPIRE_HOURS),
        )
    )
    db.commit()
    db.refresh(user)

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    activation_url = f"{frontend_url}/activate?token={raw_activation_token}"
    sent = email_service.send(
        user.email,
        "Kích hoạt tài khoản - Hệ thống đào tạo CodeGym",
        (
            f"Tài khoản của bạn đã được tạo.\n"
            f"Mật khẩu tạm: {temporary_password}\n"
            f"Liên kết kích hoạt: {activation_url}\n"
            "Sau khi đăng nhập lần đầu, vui lòng đổi mật khẩu."
        ),
    )
    result = serialize_user(user)
    result["email_sent"] = sent
    if os.getenv("APP_ENV", "development") == "development":
        result["debug_temporary_password"] = temporary_password
        result["debug_activation_token"] = raw_activation_token
    else:
        result["debug_temporary_password"] = None
        result["debug_activation_token"] = None
    return result


@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdateRequest,
    _: AuthContext = Depends(require_permission("users.update")),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.id == user_id).options(selectinload(User.roles)))
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    payload = data.model_dump(exclude_unset=True)
    if "email" in payload:
        email = str(payload["email"]).lower()
        duplicate = db.scalar(select(User).where(User.email == email, User.id != user_id))
        if duplicate:
            raise HTTPException(status_code=409, detail="Email đã tồn tại trong hệ thống.")
        payload["email"] = email
    for key, value in payload.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return serialize_user(user)


@router.put("/{user_id}/roles")
def assign_roles(
    user_id: int,
    data: AssignRolesRequest,
    context: AuthContext = Depends(require_permission("roles.assign")),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.id == user_id).options(selectinload(User.roles)))
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    roles = load_roles(db, data.role_slugs)
    current_slugs = {role.slug for role in user.roles}
    new_slugs = {role.slug for role in roles}
    if user.id == context.user.id and "system_admin" in current_slugs and "system_admin" not in new_slugs:
        raise HTTPException(status_code=400, detail="Bạn không thể tự thu hồi vai trò quản trị của chính mình.")
    if not roles:
        raise HTTPException(status_code=400, detail="Người dùng phải có ít nhất một vai trò.")
    user.roles = roles
    user.role = roles[0].slug
    db.commit()
    db.refresh(user)
    return serialize_user(user)


@router.post("/{user_id}/lock")
def lock_user(
    user_id: int,
    data: LockAccountRequest,
    context: AuthContext = Depends(require_permission("users.lock")),
    db: Session = Depends(get_db),
):
    if user_id == context.user.id:
        raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản đang đăng nhập.")
    user = db.scalar(select(User).where(User.id == user_id).options(selectinload(User.roles)))
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    now = utcnow()
    user.is_active = False
    user.status = "locked"
    user.needs_handover = True
    db.execute(
        update(AuthSession)
        .where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    db.add(AccountLockAudit(user_id=user.id, actor_user_id=context.user.id, action="lock", reason=data.reason.strip()))
    db.commit()
    return {
        "message": "Đã khóa tài khoản và thu hồi toàn bộ phiên đăng nhập.",
        "handover_warning": "Cần kiểm tra và bàn giao các lớp/công việc mà người dùng này đang phụ trách.",
        "user": serialize_user(user),
    }


@router.post("/{user_id}/unlock")
def unlock_user(
    user_id: int,
    data: UnlockAccountRequest,
    context: AuthContext = Depends(require_permission("users.lock")),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.id == user_id).options(selectinload(User.roles)))
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    user.is_active = True
    user.status = "active"
    user.needs_handover = False
    db.add(AccountLockAudit(user_id=user.id, actor_user_id=context.user.id, action="unlock", reason=data.reason.strip()))
    db.commit()
    return {"message": "Đã mở khóa tài khoản.", "user": serialize_user(user)}
