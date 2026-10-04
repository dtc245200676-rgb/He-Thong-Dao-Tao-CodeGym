import argparse

from sqlalchemy import select

from app.core.security import hash_password, validate_password
from app.db.database import SessionLocal
from app.db.seed import seed_rbac
from app.models.role import Role
from app.models.user import User


def main() -> None:
    parser = argparse.ArgumentParser(description="Tạo/cập nhật tài khoản quản trị hệ thống.")
    parser.add_argument("--email", default="admin@gmail.com")
    parser.add_argument("--password", default="12345678")
    parser.add_argument("--name", default="Quản trị viên")
    args = parser.parse_args()
    validate_password(args.password)

    db = SessionLocal()
    try:
        seed_rbac(db)
        admin_role = db.scalar(select(Role).where(Role.slug == "system_admin"))
        user = db.scalar(select(User).where(User.email == args.email.lower()))
        if user is None:
            user = User(
                full_name=args.name,
                email=args.email.lower(),
                password_hash=hash_password(args.password),
                role="system_admin",
                status="active",
                is_active=True,
                must_change_password=False,
                roles=[admin_role] if admin_role else [],
            )
            db.add(user)
            message = "Đã tạo tài khoản quản trị"
        else:
            user.full_name = user.full_name or args.name
            user.password_hash = hash_password(args.password)
            user.role = "system_admin"
            user.status = "active"
            user.is_active = True
            if admin_role and admin_role not in user.roles:
                user.roles.append(admin_role)
            message = "Đã cập nhật tài khoản hiện có thành quản trị"
        db.commit()
        print(f"{message}: {args.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
