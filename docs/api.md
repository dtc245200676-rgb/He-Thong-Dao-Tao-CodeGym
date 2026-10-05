# API Sprint 1

Base URL development: `http://127.0.0.1:8000`

Swagger: `http://127.0.0.1:8000/docs`

## Authentication

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/auth/login` | Đăng nhập |
| POST | `/api/auth/refresh` | Gia hạn access token nếu server session còn hiệu lực |
| POST | `/api/auth/logout` | Thu hồi session hiện tại |
| GET | `/api/auth/me` | Người dùng, vai trò, quyền hiện tại |
| POST | `/api/auth/forgot-password` | Yêu cầu reset mật khẩu |
| POST | `/api/auth/reset-password` | Đặt mật khẩu mới bằng token một lần |
| POST | `/api/auth/change-password` | Đổi mật khẩu khi đang đăng nhập |
| POST | `/api/auth/activate` | Kích hoạt tài khoản bằng token + mật khẩu tạm |

## User Management

Yêu cầu permission tương ứng ở backend.

| Method | Endpoint | Quyền |
|---|---|---|
| GET | `/api/users` | `users.view` |
| POST | `/api/users` | `users.create` |
| PUT | `/api/users/{id}` | `users.update` |
| PUT | `/api/users/{id}/roles` | `roles.assign` |
| POST | `/api/users/{id}/lock` | `users.lock` |
| POST | `/api/users/{id}/unlock` | `users.lock` |

`GET /api/users` hỗ trợ `q`, `role`, `status`, `page`, `page_size`; mặc định `page_size=20`.

## Roles & Permissions

| Method | Endpoint | Quyền |
|---|---|---|
| GET | `/api/roles` | `roles.view` |
| PUT | `/api/roles/{id}/permissions` | `roles.manage` |
