# Git Workflow cho nhóm 9 người

## Nguyên tắc

- Không push trực tiếp vào `main`.
- Mỗi task/sub-task Jira có branch riêng.
- Pull code mới nhất từ `main` trước khi tạo branch.
- Code xong phải test trước khi tạo Pull Request.

## Ví dụ

```bash
git checkout main
git pull origin main
git checkout -b feature/S1-08-user-management
```

Sau khi làm xong:

```bash
git add .
git commit -m "S1-08 implement user management"
git push -u origin feature/S1-08-user-management
```

Tạo Pull Request từ branch vào `main`, nhờ ít nhất một thành viên review rồi merge.

## Sau khi merge

```bash
git checkout main
git pull origin main
git branch -d feature/S1-08-user-management
```
