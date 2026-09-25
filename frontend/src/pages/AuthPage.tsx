import { useState, type FormEvent } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { ShieldIcon } from '../components/Icons'

interface Props {
  mode: 'login' | 'register'
}

export function AuthPage({ mode }: Props) {
  const { user, ready, login, register } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const isRegister = mode === 'register'

  if (!ready) return <div className="auth-screen"><div className="page-state"><span className="spinner" /><p>Đang tải...</p></div></div>
  if (user) return <Navigate to="/" replace />

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    if (!username.trim() || !password) {
      setError('Vui lòng nhập tên đăng nhập và mật khẩu.')
      return
    }
    if (isRegister && password !== confirm) {
      setError('Mật khẩu xác nhận không khớp.')
      return
    }
    setSaving(true)
    try {
      if (isRegister) await register(username.trim(), password)
      else await login(username.trim(), password)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Không thể hoàn tất yêu cầu.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="auth-screen">
      <section className="auth-card">
        <div className="auth-brand">
          <span className="brand-mark"><ShieldIcon size={25} /></span>
          <div>
            <strong>PHÁT HIỆN KHÔNG ĐỘI MŨ</strong>
            <small>{isRegister ? 'Tạo tài khoản để quản lý dự án' : 'Đăng nhập để tiếp tục'}</small>
          </div>
        </div>
        <h1>{isRegister ? 'Đăng ký' : 'Đăng nhập'}</h1>
        <form className="form-stack" onSubmit={submit}>
          <label>
            <span>Tên đăng nhập</span>
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              autoComplete="username"
              placeholder="ví dụ: nguyenvana"
              autoFocus
            />
          </label>
          <label>
            <span>Mật khẩu</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              placeholder={isRegister ? 'Tối thiểu 6 ký tự' : 'Nhập mật khẩu'}
            />
          </label>
          {isRegister && (
            <label>
              <span>Xác nhận mật khẩu</span>
              <input
                type="password"
                value={confirm}
                onChange={(event) => setConfirm(event.target.value)}
                autoComplete="new-password"
                placeholder="Nhập lại mật khẩu"
              />
            </label>
          )}
          {error && <div className="alert alert-danger">{error}</div>}
          <button type="submit" className="button button-primary button-large" disabled={saving}>
            {saving ? 'Đang xử lý...' : isRegister ? 'Tạo tài khoản' : 'Đăng nhập'}
          </button>
        </form>
        <p className="auth-switch">
          {isRegister ? (
            <>Đã có tài khoản? <Link to="/login">Đăng nhập</Link></>
          ) : (
            <>Chưa có tài khoản? <Link to="/register">Đăng ký</Link></>
          )}
        </p>
      </section>
    </div>
  )
}
