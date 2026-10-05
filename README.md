# Hệ Thống Đào Tạo CodeGym

Dự án Scrum nhóm 9 thành viên. Repository này chứa Frontend React và Backend FastAPI dùng chung một cơ sở dữ liệu MySQL.

## Công nghệ

- Frontend: React + TypeScript + Vite + Ant Design + Axios + React Router
- Backend: Python 3.12 + FastAPI
- Database: MySQL qua XAMPP, InnoDB, utf8mb4
- ORM / Migration: SQLAlchemy 2.0 + Alembic
- Xác thực: JWT + bcrypt + session phía server
- Test: pytest

## Sprint 1 đã triển khai

Sprint 1 tập trung vào tài khoản, phân quyền và quản trị người dùng:

- S1-01: Đăng nhập bằng email/mật khẩu, JWT, khóa tạm 15 phút sau 5 lần sai
- S1-02: Đăng xuất phía server, session trượt và tự gia hạn khi người dùng còn hoạt động
- S1-03: Quên mật khẩu, token 30 phút, dùng một lần, phản hồi chống dò tài khoản
- S1-04: Đổi mật khẩu, bắt buộc mật khẩu hiện tại, mật khẩu mới >= 8 ký tự có chữ + số, thu hồi phiên khác
- S1-05: RBAC 8 vai trò, quyền kiểm tra ở backend, mặc định từ chối
- S1-06: Menu Frontend theo quyền, hiển thị tên + vai trò, responsive ở màn hình nhỏ
- S1-07: Trang 403 thống nhất, thông báo tiếng Việt và nút quay lại luồng làm việc
- S1-08: Tạo/sửa/tìm người dùng, lọc vai trò/trạng thái, 20 dòng/trang, email kích hoạt + mật khẩu tạm
- S1-09: Một người có nhiều vai trò, thay đổi có hiệu lực ngay ở request kế tiếp, không tự thu hồi vai trò admin
- S1-10: Khóa/mở khóa tài khoản, bắt buộc lý do, thu hồi session và cảnh báo bàn giao

Chi tiết Acceptance Criteria: `docs/sprint-1.md`.

## Cấu trúc

```text
He-Thong-Dao-Tao-CodeGym/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── scripts/
│   ├── tests/
│   ├── alembic.ini
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── components/
│   │   ├── layouts/
│   │   └── pages/
│   └── .env.example
├── docs/
├── .gitignore
└── README.md
```

## Chạy MySQL

1. Mở XAMPP và Start `MySQL`.
2. Trong phpMyAdmin tạo database `he_thong_dao_tao` với charset/collation utf8mb4.
3. Copy `backend/.env.example` thành `backend/.env` và chỉnh `DATABASE_URL` nếu MySQL của bạn có mật khẩu.

Ví dụ mặc định XAMPP:

```env
DATABASE_URL=mysql+pymysql://root:@localhost:3306/he_thong_dao_tao?charset=utf8mb4
```

## Chạy Backend lần đầu

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m scripts.create_admin --email admin@gmail.com --password 12345678 --name "Quản trị viên"
python -m uvicorn app.main:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`

> Nếu database đã có bảng `users` từ bản S1-01 cũ, migration đầu tiên sẽ giữ dữ liệu cũ và bổ sung các cột/bảng mới.

## Chạy Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

## Email trong môi trường local

Nếu chưa cấu hình SMTP, Backend không gửi mail thật mà in nội dung email và link reset/kích hoạt ra Terminal. Để gửi mail thật, điền các biến `SMTP_*` trong `backend/.env`.

## Test Backend

```powershell
cd backend
pytest -q
```

Bộ test Sprint 1 hiện kiểm tra đăng nhập, khóa sau 5 lần sai, reset password dùng một lần, logout thu hồi session, RBAC tối thiểu 3 vai trò, gán vai trò và quản trị tài khoản.

## Git Workflow

Không push trực tiếp vào `main`.

```text
Jira task
  -> feature branch
  -> code + test
  -> commit
  -> push
  -> Pull Request
  -> review
  -> merge vào main
```

Ví dụ branch: `feature/S1-08-user-management`.
