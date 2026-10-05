# Database Sprint 1

- Database: MySQL
- Engine: InnoDB
- Charset: utf8mb4
- ORM: SQLAlchemy 2.0
- Migration: Alembic

## Bảng

| Bảng | Mục đích |
|---|---|
| `users` | Tài khoản, trạng thái, khóa tạm, thông tin cơ bản |
| `roles` | 8 vai trò nghiệp vụ |
| `permissions` | Danh mục quyền chức năng |
| `user_roles` | Quan hệ nhiều-nhiều User ↔ Role |
| `role_permissions` | Quan hệ nhiều-nhiều Role ↔ Permission |
| `auth_sessions` | Session phía server, hỗ trợ logout/revoke/gia hạn |
| `password_reset_tokens` | Token reset mật khẩu 30 phút, một lần |
| `activation_tokens` | Token kích hoạt tài khoản |
| `account_lock_audits` | Lý do và người thực hiện khóa/mở khóa |

## Migration

Trong thư mục `backend`:

```powershell
alembic upgrade head
```

Migration `20261004_0001` hỗ trợ cả database mới lẫn database dev đã có bảng `users` từ S1-01 ban đầu.
