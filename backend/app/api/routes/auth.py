from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    verify_password
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

INVALID_LOGIN_MESSAGE = (
    "Email hoặc mật khẩu không đúng"
)


@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    # Không cho biết email có tồn tại hay không
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_LOGIN_MESSAGE
        )

    now = datetime.utcnow()

    # Tài khoản đang bị khóa tạm thời
    if (
        user.locked_until is not None
        and user.locked_until > now
    ):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=(
                "Tài khoản tạm thời bị khóa. "
                "Vui lòng thử lại sau."
            )
        )

    # Đã hết 15 phút
    if (
        user.locked_until is not None
        and user.locked_until <= now
    ):
        user.failed_login_attempts = 0
        user.locked_until = None

        db.commit()

    # Sai mật khẩu
    if not verify_password(
        data.password,
        user.password_hash
    ):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= 5:
            user.failed_login_attempts = 0
            user.locked_until = (
                now + timedelta(minutes=15)
            )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_LOGIN_MESSAGE
        )

    # Tài khoản bị admin khóa
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa"
        )

    # Login đúng
    user.failed_login_attempts = 0
    user.locked_until = None

    db.commit()

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role
    )

    return LoginResponse(
        access_token=access_token,
        role=user.role,
        message="Đăng nhập thành công"
    )