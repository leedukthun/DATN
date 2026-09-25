import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { UploadModal } from '../components/UploadModal'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../services/api'
import type { Analysis, Project } from '../types'

export function UploadPage() {
  const [params, setParams] = useSearchParams()
  const [projects, setProjects] = useState<Project[]>([])
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const sessionId = Number(params.get('session'))
  useEffect(() => {
    let cancelled = false
    api.projects().then(rows => { if (!cancelled) setProjects(rows) }).catch(e => { if (!cancelled) setError(e.message) }).finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])
  useEffect(() => {
    if (!sessionId) return
    let cancelled = false
    let timer: number | undefined
    const poll = async () => {
      try {
        const row = await api.analysis(sessionId)
        if (cancelled) return
        setAnalysis(row); setError('')
        if (row.status === 'PENDING' || row.status === 'PROCESSING') timer = window.setTimeout(poll, 1800)
      } catch (e) {
        if (!cancelled) { setError(e instanceof Error ? e.message : 'Không thể cập nhật tiến trình.'); timer = window.setTimeout(poll, 4000) }
      }
    }
    void poll()
    return () => { cancelled = true; window.clearTimeout(timer) }
  }, [sessionId])
  return <div className="sketch-page">
    <div className="sketch-title"><h1>Phân tích ảnh, video</h1></div>
    {error && <div className="alert alert-danger" role="alert">{error}</div>}
    <div className="sketch-columns upload-columns">
      <section className="panel upload-inline" aria-label="Tải dữ liệu">
        {loading ? <p>Đang tải dự án...</p> : !projects.length ? <p>Chưa có dự án. <Link className="row-link" to="/">Tạo dự án và địa điểm</Link> trước khi tải dữ liệu.</p> :
          <UploadModal inline open projects={projects} initialProjectId={Number(params.get('project')) || undefined} initialLocationId={Number(params.get('location')) || undefined} onClose={() => {}} onAnalysisCreated={row => { setAnalysis(row); setParams({ session: String(row.id) }) }} />}
      </section>
      <section className="panel progress-panel" aria-live="polite">
        <h2>Tiến trình phân tích</h2>
        <div className="sketch-row-heading">{analysis ? <StatusBadge status={analysis.status} /> : <span>Chưa bắt đầu</span>}<strong>{analysis?.progress || 0}%</strong></div>
        <div className="progress-track large" role="progressbar" aria-label="Tiến trình phân tích" aria-valuemin={0} aria-valuemax={100} aria-valuenow={analysis?.progress || 0}><div style={{ width: `${analysis?.progress || 0}%` }} /></div>
        <div className="processing-files">{analysis?.media_files?.map(file => <div key={file.id}><span>{file.original_filename}</span><StatusBadge status={file.status} /></div>)}</div>
        {analysis?.error_message && <div className="alert alert-danger">{analysis.error_message}</div>}
        <p className="progress-message">{analysis ? `Đã xử lý ${analysis.processed_files}/${analysis.total_files} tệp.` : 'Chọn ảnh hoặc video rồi bấm Bắt đầu phân tích. Tiến trình sẽ tự động cập nhật tại đây.'}</p>
        {analysis && ['COMPLETED', 'FAILED'].includes(analysis.status) ? <Link className="button button-outline button-wide" to={`/analyses/${analysis.id}`}>Xem kết quả</Link> : <button className="button button-outline button-wide" disabled>Xem kết quả khi hoàn tất</button>}
      </section>
    </div>
  </div>
}
