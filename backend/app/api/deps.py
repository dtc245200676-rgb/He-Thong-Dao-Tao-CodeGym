from dataclasses import dataclass
from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import SESSION_EXPIRE_MINUTES, decode_access_token, utcnow
from app.db.database import get_db
from app.models.role import Role
from app.models.session import AuthSession
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    user: User
    session: AuthSession
    role_slugs: list[str]
    permissions: set[str]


def _credentials_or_401(credentials: HTTPAuthorizationCredentials | None) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng đăng nhập để tiếp tục.",
        )
    return credentials.credentials


def get_current_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthContext:
    token = _credentials_or_401(credentials)
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        code = str(exc)
        message = "Phiên đăng nhập đã hết hạn." if code == "TOKEN_EXPIRED" else "Phiên đăng nhập không hợp lệ."
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": code, "message": message},
        ) from exc

    user_id = int(payload.get("sub", 0))
    session_id = payload.get("sid")
    if not user_id or not session_id:
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ.")

    session = db.get(AuthSession, session_id)
    now = utcnow()
    if session is None or session.user_id != user_id or session.revoked_at is not None or session.expires_at <= now:
        raise HTTPException(
            status_code=401,
            detail={"code": "SESSION_EXPIRED", "message": "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại."},
        )

    user = db.scalar(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    if user is None:
        raise HTTPException(status_code=401, detail="Tài khoản không tồn tại.")
    if not user.is_active or user.status != "active":
        session.revoked_at = now
        db.commit()
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa hoặc chưa kích hoạt.")

    # Sliding server-side session: active users keep their session alive.
    session.last_activity_at = now
    session.expires_at = now + timedelta(minutes=SESSION_EXPIRE_MINUTES)
    db.commit()

    role_slugs = [role.slug for role in user.roles]
    permissions = {permission.code for role in user.roles for permission in role.permissions}
    return AuthContext(user=user, session=session, role_slugs=role_slugs, permissions=permissions)


def require_permission(permission_code: str):
    def dependency(context: AuthContext = Depends(get_current_context)) -> AuthContext:
        if permission_code not in context.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện chức năng này.",
            )
        return context

    return dependency
