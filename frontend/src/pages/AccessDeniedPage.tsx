import { Button, Result } from 'antd'
import { useNavigate } from 'react-router-dom'

export default function AccessDeniedPage() {
  const navigate = useNavigate()
  return <div className="page-center"><Result status="403" title="Bạn không có quyền truy cập" subTitle="Chức năng này không thuộc quyền của vai trò hiện tại. Hãy quay lại trang làm việc phù hợp." extra={<Button type="primary" onClick={() => navigate('/dashboard')}>Về trang tổng quan</Button>} /></div>
}
