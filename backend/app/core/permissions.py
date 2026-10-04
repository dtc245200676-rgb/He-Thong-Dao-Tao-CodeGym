PERMISSIONS = {
    "dashboard.view": "Xem trang tổng quan",
    "users.view": "Xem danh sách người dùng",
    "users.create": "Tạo tài khoản người dùng",
    "users.update": "Sửa thông tin người dùng",
    "users.lock": "Khóa/mở khóa tài khoản",
    "roles.view": "Xem vai trò và quyền",
    "roles.manage": "Cấu hình quyền theo vai trò",
    "roles.assign": "Gán/thu hồi vai trò",
    "training.view": "Xem dữ liệu đào tạo",
    "training.edit": "Cập nhật dữ liệu đào tạo",
    "grades.view": "Xem điểm",
    "grades.edit": "Sửa điểm",
    "tuition.view": "Xem học phí",
    "tuition.edit": "Sửa học phí",
}

ROLE_DEFINITIONS = {
    "system_admin": {
        "name": "Quản trị hệ thống",
        "description": "Quản trị tài khoản, vai trò và toàn bộ cấu hình hệ thống.",
        "permissions": list(PERMISSIONS.keys()),
    },
    "training_manager": {
        "name": "Quản lý đào tạo",
        "description": "Quản lý hoạt động đào tạo, lớp học và nghiệp vụ học vụ.",
        "permissions": [
            "dashboard.view",
            "users.view",
            "training.view",
            "training.edit",
            "grades.view",
            "grades.edit",
            "tuition.view",
        ],
    },
    "teacher": {
        "name": "Giảng viên",
        "description": "Giảng dạy, theo dõi lớp và nhập điểm; không sửa học phí.",
        "permissions": [
            "dashboard.view",
            "training.view",
            "grades.view",
            "grades.edit",
            "tuition.view",
        ],
    },
    "accountant": {
        "name": "Kế toán",
        "description": "Quản lý học phí; không sửa điểm.",
        "permissions": [
            "dashboard.view",
            "users.view",
            "tuition.view",
            "tuition.edit",
            "grades.view",
        ],
    },
    "academic_affairs": {
        "name": "Giáo vụ",
        "description": "Hỗ trợ vận hành đào tạo và hồ sơ học vụ.",
        "permissions": [
            "dashboard.view",
            "users.view",
            "training.view",
            "training.edit",
            "grades.view",
        ],
    },
    "admissions": {
        "name": "Tuyển sinh",
        "description": "Theo dõi và hỗ trợ hồ sơ đầu vào.",
        "permissions": ["dashboard.view", "users.view", "training.view"],
    },
    "student_services": {
        "name": "Công tác sinh viên",
        "description": "Hỗ trợ người học trong quá trình học tập.",
        "permissions": ["dashboard.view", "users.view", "training.view", "grades.view"],
    },
    "student": {
        "name": "Học viên",
        "description": "Xem thông tin học tập, điểm và học phí của bản thân.",
        "permissions": ["dashboard.view", "training.view", "grades.view", "tuition.view"],
    },
}

LEGACY_ROLE_ALIASES = {
    "admin": "system_admin",
    "user": "student",
    "teacher": "teacher",
    "accountant": "accountant",
}
