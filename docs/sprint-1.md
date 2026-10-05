# Sprint 1 — Tài khoản, phân quyền và quản trị người dùng

## Sprint Goal

Người dùng đăng nhập/đăng xuất an toàn, tự phục hồi tài khoản; quản trị viên quản lý tài khoản và phân quyền; giao diện chỉ hiển thị chức năng phù hợp với quyền.

## S1-01 — Đăng nhập

- Đăng nhập đúng chuyển vào hệ thống và trả vai trò.
- Sai email/mật khẩu trả cùng thông báo `Email hoặc mật khẩu không đúng` để tránh dò tài khoản.
- Tài khoản bị khóa tạm 15 phút sau 5 lần sai liên tiếp.
- JWT chỉ dùng để nhận diện; backend vẫn kiểm tra session phía server ở mỗi request.

## S1-02 — Đăng xuất và phiên

- Session phía server được gia hạn theo hoạt động.
- Logout đánh dấu session bị thu hồi ngay lập tức.
- Frontend tự refresh access token khi session còn hiệu lực.
- Session hết hạn chuyển về Login với thông báo rõ ràng.
- Các form chính lưu draft trong `sessionStorage` để giảm mất dữ liệu khi phải đăng nhập lại.

## S1-03 — Quên mật khẩu

- Nhập email tạo token reset có hiệu lực 30 phút.
- Token chỉ dùng một lần.
- Email tồn tại/không tồn tại đều nhận cùng một response công khai.
- Nếu SMTP chưa cấu hình, link reset được in ra Terminal ở môi trường development.

## S1-04 — Đổi mật khẩu

- Bắt buộc nhập mật khẩu hiện tại.
- Mật khẩu mới tối thiểu 8 ký tự, có ít nhất một chữ và một số.
- Sau khi đổi, tất cả session khác của tài khoản bị thu hồi.

## S1-05 — RBAC

Hệ thống seed 8 vai trò nghiệp vụ:

1. Quản trị hệ thống
2. Quản lý đào tạo
3. Giảng viên
4. Kế toán
5. Giáo vụ
6. Tuyển sinh
7. Công tác sinh viên
8. Học viên

- Mỗi chức năng backend dùng dependency kiểm quyền.
- Không có quyền thì mặc định từ chối với thông báo tiếng Việt.
- Giảng viên không có `tuition.edit`; kế toán không có `grades.edit`.
- Có pytest cho ít nhất 3 vai trò.

## S1-06 — Menu theo quyền

- Menu không có quyền sẽ không hiển thị.
- Header hiển thị tên và các vai trò của người đăng nhập.
- Layout chuyển sang Drawer trên màn hình nhỏ, dùng được ở khoảng 360px.

## S1-07 — Thông báo lỗi quyền

- Trang 403 thống nhất với giao diện chung.
- Có thông báo rõ ràng và nút quay về trang tổng quan.

## S1-08 — Quản lý người dùng

- Tạo tài khoản với mật khẩu tạm + link kích hoạt.
- Email trùng bị từ chối bằng thông báo cụ thể.
- Sửa họ tên/email/số điện thoại.
- Tìm theo tên, email, số điện thoại.
- Lọc theo vai trò và trạng thái.
- Mặc định 20 dòng/trang.

## S1-09 — Gán/thu hồi vai trò

- Một người dùng có thể có nhiều vai trò.
- Backend đọc quyền trực tiếp từ database ở mỗi request, nên thay đổi có hiệu lực ngay ở thao tác kế tiếp.
- Người dùng không thể tự thu hồi vai trò `system_admin` của chính mình.

## S1-10 — Khóa/mở khóa

- Tài khoản khóa không đăng nhập được.
- Khi khóa, toàn bộ session đang mở bị thu hồi.
- Bắt buộc nhập lý do khóa/mở khóa và ghi audit.
- Đánh dấu `needs_handover` để giao diện cảnh báo cần bàn giao lớp/công việc phụ trách.
