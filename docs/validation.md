# Kiểm tra trước khi bàn giao Sprint 1

Đã chạy trong môi trường kiểm tra:

- `pytest -q`: **7 passed**
- TypeScript: `tsc -b`: **pass**
- Alembic migration trên database mới: **pass**
- Alembic migration trên database có sẵn bảng `users` prototype: **pass**

Lưu ý: MySQL/XAMPP chạy trên máy thành viên nên cần chạy `alembic upgrade head` và test lại Swagger/Frontend trên máy local sau khi giải nén.
