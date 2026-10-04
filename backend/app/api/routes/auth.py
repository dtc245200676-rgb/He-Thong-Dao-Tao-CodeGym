import os
import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, bearer_scheme, get_current_context
from app.core.security import (
    ACTIVATION_TOKEN_EXPIRE_HOURS,
    RESET_TOKEN_EXPIRE_MINUTES,
    SESSION_EXPIRE_MINUTES,
    create_access_token,
    decode_access_token,
    generate_one_time_token,
    hash_one_time_token,
    hash_password,
    utcnow,
    validate_password,
    verify_password,
)
from app.db.database import get_db
from app.models.role import Role
from app.models.session import AuthSession
from app.models.tokens import ActivationToken, PasswordResetToken
from app.models.user import User
from app.schemas.auth import (
    ActivateAccountRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    ResetPasswordRequest,
)
from app.services.email_service import email_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
INVALID_LOGIN_MESSAGE = "Email hoặc mật khẩu không đúng"
GENERIC_RESET_MESSAGE = "Nếu email tồn tại trong hệ thống, hướng dẫn đặt lại mật khẩu đã được gửi."


def _roles(user: User) -> list[str]:
    result = [role.slug for role in user.roles]
    if not result and user.role:
        result = [user.role]
    return result


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.scalar(
        select(User)
        .where(User.email == data.email.lower())
        .options(selectinload(User.roles))
    )
    if user is None:
        raise HTTPException(status_code=401, detail=INVALID_LOGIN_MESSAGE)

    now = utcnow()
    if user.locked_until and user.locked_until > now:
        raise HTTPException(status_code=423, detail="Tài khoản tạm thời bị khóa 15 phút do đăng nhập sai nhiều lần.")
    if user.locked_until and user.locked_until <= now:
        user.failed_login_attempts = 0
        user.locked_until = None

    if not verify_password(data.password, user.password_hash):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.failed_login_attempts = 0
            user.locked_until = now + timedelta(minutes=15)
        db.commit()
        raise HTTPException(status_code=401, detail=INVALID_LOGIN_MESSAGE)

    if not user.is_active or user.status == "locked":
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa.")
    if user.status == "pending":
        raise HTTPException(status_code=403, detail="Tài khoản chưa được kích hoạt.")

    user.failed_login_attempts = 0
    user.locked_until = None

    session = AuthSession(
        id=str(uuid.uuid4()),
        user_id=user.id,
        expires_at=now + timedelta(minutes=SESSION_EXPIRE_MINUTES),
        last_activity_at=now,
        user_agent=request.headers.get("user-agent", "")[:255],
    )
    db.add(session)
    db.commit()

    roles = _roles(user)
    token = create_access_token(user.id, session.id, roles)
    return LoginResponse(
        access_token=token,
        role=roles[0] if roles else user.role,
        roles=roles,
        must_change_password=user.must_change_password,
        message="Đăng nhập thành công",
    )


@router.post("/refresh", response_model=LoginResponse)
def refresh_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Thiếu phiên đăng nhập.")
    try:
        payload = decode_access_token(credentials.credentials, verify_exp=False)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Phiên đăng nhập không hợp lệ.") from exc

    session = db.get(AuthSession, payload.get("sid"))
    user_id = int(payload.get("sub", 0))
    now = utcnow()
    if not session or session.user_id != user_id or session.revoked_at is not None or session.expires_at <= now:
        raise HTTPException(status_code=401, detail={"code": "SESSION_EXPIRED", "message": "Phiên đăng nhập đã hết hạn."})

    user = db.scalar(select(User).where(User.id == user_id).options(selectinload(User.roles)))
    if not user or not user.is_active or user.status != "active":
        raise HTTPException(status_code=403, detail="Tài khoản không còn quyền truy cập.")

    session.last_activity_at = now
    session.expires_at = now + timedelta(minutes=SESSION_EXPIRE_MINUTES)
    db.commit()

    roles = _roles(user)
    token = create_access_token(user.id, session.id, roles)
    return LoginResponse(
        access_token=token,
        role=roles[0] if roles else user.role,
        roles=roles,
        must_change_password=user.must_change_password,
        message="Phiên đăng nhập đã được gia hạn",
    )


@router.post("/logout", response_model=MessageResponse)
def logout(context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    context.session.revoked_at = utcnow()
    db.commit()
    return MessageResponse(message="Đăng xuất thành công")


@router.get("/me")
def me(context: AuthContext = Depends(get_current_context)):
    user = context.user
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "roles": context.role_slugs,
        "permissions": sorted(context.permissions),
        "must_change_password": user.must_change_password,
    }


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if user:
        now = utcnow()
        db.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None))
            .values(used_at=now)
        )
        raw_token = generate_one_time_token()
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_one_time_token(raw_token),
                expires_at=now + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
            )
        )
        db.commit()
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        reset_url = f"{frontend_url}/reset-password?token={raw_token}"
        email_service.send(
            user.email,
            "Đặt lại mật khẩu - Hệ thống đào tạo CodeGym",
            f"Liên kết đặt lại mật khẩu có hiệu lực {RESET_TOKEN_EXPIRE_MINUTES} phút và chỉ dùng một lần:\n{reset_url}",
        )
    return ForgotPasswordResponse(message=GENERIC_RESET_MESSAGE)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        validate_password(data.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    token = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_one_time_token(data.token),
            PasswordResetToken.used_at.is_(None),
        )
    )
    now = utcnow()
    if not token or token.expires_at <= now:
        raise HTTPException(status_code=400, detail="Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.")

    user = db.get(User, token.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Liên kết đặt lại mật khẩu không hợp lệ.")

    user.password_hash = hash_password(data.new_password)
    user.must_change_password = False
    user.failed_login_attempts = 0
    user.locked_until = None
    token.used_at = now
    db.execute(
        update(AuthSession)
        .where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    db.commit()
    return MessageResponse(message="Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại.")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    data: ChangePasswordRequest,
    context: AuthContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, context.user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng.")
    try:
        validate_password(data.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if verify_password(data.new_password, context.user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải khác mật khẩu hiện tại.")

    context.user.password_hash = hash_password(data.new_password)
    context.user.must_change_password = False
    now = utcnow()
    db.execute(
        update(AuthSession)
        .where(
            AuthSession.user_id == context.user.id,
            AuthSession.id != context.session.id,
            AuthSession.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )
    db.commit()
    return MessageResponse(message="Đổi mật khẩu thành công. Các phiên đăng nhập khác đã bị thu hồi.")


@router.post("/activate", response_model=MessageResponse)
def activate_account(data: ActivateAccountRequest, db: Session = Depends(get_db)):
    token = db.scalar(
        select(ActivationToken).where(
            ActivationToken.token_hash == hash_one_time_token(data.token),
            ActivationToken.used_at.is_(None),
        )
    )
    now = utcnow()
    if not token or token.expires_at <= now:
        raise HTTPException(status_code=400, detail="Liên kết kích hoạt không hợp lệ hoặc đã hết hạn.")
    user = db.get(User, token.user_id)
    if not user or not verify_password(data.temporary_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu tạm không đúng.")

    user.is_active = True
    user.status = "active"
    user.must_change_password = True
    token.used_at = now
    db.commit()
    return MessageResponse(message="Kích hoạt tài khoản thành công. Hãy đăng nhập và đổi mật khẩu tạm.")
