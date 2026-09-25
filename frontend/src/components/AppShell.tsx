import { useEffect, useRef } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { ChartIcon, EyeIcon, FolderIcon, ShieldIcon, UploadIcon } from './Icons'

export function AppShell() {
  const { user, logout } = useAuth()
  const { pathname } = useLocation()
  const contentRef = useRef<HTMLElement>(null)
  useEffect(() => {
    contentRef.current?.scrollTo({ top: 0, left: 0 })
  }, [pathname])
  const active = pathname.startsWith('/upload') ? 'upload' : pathname.startsWith('/analyses') || pathname.startsWith('/results') ? 'results' : pathname.startsWith('/statistics') || pathname.endsWith('/hourly-stats') ? 'statistics' : 'projects'
  return <div className="app-shell sketch-shell">
    <header className="topbar sketch-header">
      <Link to="/" className="brand"><span className="brand-mark"><ShieldIcon size={25} /></span><span><strong>PHÁT HIỆN KHÔNG ĐỘI MŨ</strong><small>Lê Đức Thuận - DATN</small></span></Link>
      <div className="account-pill"><span className="online-dot" /><strong>{user?.username}</strong><button className="text-button logout-button" onClick={logout}>Đăng xuất</button></div>
    </header>
    <div className="sketch-layout">
      <nav className="sketch-sidebar topnav" aria-label="Điều hướng chính">
        {[
          ['projects', '/', 'Dự án'], ['upload', '/upload', 'Phân tích dữ liệu'],
          ['results', '/results', 'Kết quả'], ['statistics', '/statistics', 'Thống kê'],
        ].map(([key, to, label]) => <Link key={key} to={to} className={active === key ? 'active' : ''} aria-current={active === key ? 'page' : undefined}>{key === 'projects' ? <FolderIcon size={19} /> : key === 'upload' ? <UploadIcon size={19} /> : key === 'results' ? <EyeIcon size={19} /> : <ChartIcon size={19} />}{label}</Link>)}
      </nav>
      <main className="sketch-main" ref={contentRef} tabIndex={0} aria-label="Nội dung trang"><Outlet /></main>
    </div>
  </div>
}
