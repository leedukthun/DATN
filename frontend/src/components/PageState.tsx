import { RefreshIcon } from './Icons'

export function LoadingPage({ text = 'Đang tải dữ liệu...' }: { text?: string }) {
  return <div className="page-state"><span className="spinner" /><p>{text}</p></div>
}

export function ErrorPage({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="page-state error-page">
      <div className="error-symbol">!</div>
      <h2>Không thể tải dữ liệu</h2>
      <p>{message}</p>
      {onRetry && <button className="button button-primary" onClick={onRetry}><RefreshIcon size={18} /> Thử lại</button>}
    </div>
  )
}
