import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ErrorPage, LoadingPage } from '../components/PageState'
import { Modal } from '../components/Modal'
import { StatCard } from '../components/StatCard'
import { StatusBadge } from '../components/StatusBadge'
import { api, assetUrl } from '../services/api'
import type { Analysis } from '../types'
import { formatDate, formatPercent, formatTimestamp } from '../utils'

export function AnalysisDetail() {
  const { analysisId } = useParams()
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [reload, setReload] = useState(0)
  const [mediaId, setMediaId] = useState<number | null>(null)
  const [violationId, setViolationId] = useState<number | null>(null)
  const [original, setOriginal] = useState(false)
  const [details, setDetails] = useState(false)
  useEffect(() => {
    let cancelled = false
    let timer: number | undefined
    setLoading(true); setAnalysis(null); setError(''); setMediaId(null); setViolationId(null)
    const load = async () => {
      try {
        const row = await api.analysis(Number(analysisId))
        if (cancelled) return
        setAnalysis(row); setError('')
        if (['PENDING', 'PROCESSING'].includes(row.status)) timer = window.setTimeout(load, 1800)
      } catch (e) { if (!cancelled) setError(e instanceof Error ? e.message : 'Không thể tải kết quả.') }
      finally { if (!cancelled) setLoading(false) }
    }
    void load()
    return () => { cancelled = true; window.clearTimeout(timer) }
  }, [analysisId, reload])
  if (loading) return <LoadingPage text="Đang tải kết quả..." />
  if (!analysis) return <ErrorPage message={error || 'Không tìm thấy phiên phân tích.'} onRetry={() => setReload(v => v + 1)} />
  const media = analysis.media_files || []
  const selectedMedia = media.find(m => m.id === mediaId) || media[0]
  const violations = (analysis.violations || []).filter(v => v.media_id === selectedMedia?.id)
  const selectedViolation = violations.find(v => v.id === violationId) || violations[0]
  const source = selectedMedia && (original ? selectedMedia.original_url : selectedMedia.result_url)
  return <div className="sketch-page">
    <div className="sketch-title"><h1>Kết quả nhận diện</h1><span className="muted"><Link to={`/?project=${analysis.project_id}`}>{analysis.project_name}</Link> / <Link to={`/locations/${analysis.location_id}`}>{analysis.location_name}</Link> / Phiên {analysis.id}</span></div>
    <div className="sketch-result-meta"><span>{formatDate(analysis.analysis_date)}</span><StatusBadge status={analysis.status} /><Link className="row-link" to={`/upload?session=${analysis.id}`}>Xem tiến trình</Link><a className="row-link" href={api.downloadAnalysisUrl(analysis.id)}>Tải kết quả ZIP</a></div>
    {error && <div className="alert alert-danger">{error}<button className="text-button" onClick={() => setReload(v => v + 1)}>Thử lại</button></div>}
    {analysis.error_message && <div className="alert alert-danger">{analysis.error_message}</div>}
    <section className="stats-grid"><StatCard label="Tổng đối tượng" value={analysis.total_vehicles} /><StatCard label="Có mũ" tone="success" value={analysis.helmet_count} /><StatCard label="Không mũ" tone="danger" value={analysis.no_helmet_count} /><StatCard label="Tỷ lệ không mũ" tone="warning" value={formatPercent(analysis.violation_rate)} /></section>
    <div className="sketch-columns result-columns">
      <section className="sketch-media-panel" aria-label="Ảnh và video kết quả">
        <div className="sketch-media-toolbar">
          <label><span className="sr-only">Tệp dữ liệu</span><select value={selectedMedia?.id || ''} onChange={e => { setMediaId(Number(e.target.value)); setViolationId(null) }}>{media.map(m => <option key={m.id} value={m.id}>{m.original_filename}</option>)}</select></label>
          <div className="sketch-actions"><button className={`button ${original ? 'button-primary' : 'button-outline'}`} aria-pressed={original} onClick={() => setOriginal(true)}>Bản gốc</button><button className={`button ${!original ? 'button-primary' : 'button-outline'}`} aria-pressed={!original} onClick={() => setOriginal(false)}>Đã nhận diện</button></div>
        </div>
        <div className="sketch-media-view">
          {source ? selectedMedia?.file_type === 'video' ? <video key={source} controls preload="metadata" src={assetUrl(source)} /> : <img src={assetUrl(source)} alt={original ? 'Ảnh gốc' : 'Ảnh đã nhận diện'} /> : <div className="sketch-placeholder">{selectedMedia?.status === 'FAILED' ? selectedMedia.error_message || 'Xử lý tệp thất bại.' : `Chưa có kết quả. Tiến trình: ${selectedMedia?.progress || 0}%`}</div>}
        </div>
        {selectedMedia && <p className="muted">{selectedMedia.original_filename} · <StatusBadge status={selectedMedia.status} /></p>}
      </section>
      <aside className="panel sketch-evidence"><h2>Minh chứng không đội mũ</h2>
        {violations.length ? <>
          <div className="sketch-evidence-grid">{violations.map(v => <button key={v.id} className={`sketch-evidence-item ${v.id === selectedViolation?.id ? 'selected' : ''}`} onClick={() => setViolationId(v.id)} aria-label={`Chọn minh chứng ${v.vehicle_id || v.id}`} aria-pressed={v.id === selectedViolation?.id}><img src={assetUrl(v.evidence_url)} alt={`Minh chứng ${v.vehicle_id || v.id}`} loading="lazy" /><span>{v.vehicle_id || `Vi phạm ${v.id}`}</span></button>)}</div>
          <p>Mã theo dõi: <strong>{selectedViolation?.vehicle_id || '—'}</strong></p><p>Khung hình / thời điểm: <strong>{selectedViolation?.frame_number ?? 'Ảnh tĩnh'} / {formatTimestamp(selectedViolation?.timestamp_seconds ?? null)}</strong></p><p>Độ tin cậy: <strong>{((selectedViolation?.confidence || 0) * 100).toFixed(1)}%</strong></p>
          <button className="button button-outline button-wide" onClick={() => setDetails(true)}>Xem chi tiết minh chứng</button>
        </> : <p className="muted">{analysis.status === 'COMPLETED' ? 'Không có minh chứng không đội mũ cho tệp này.' : 'Minh chứng sẽ xuất hiện sau khi tệp được xử lý.'}</p>}
      </aside>
    </div>
    <Modal open={details && Boolean(selectedViolation)} onClose={() => setDetails(false)} title="Chi tiết minh chứng" size="large">
      {selectedViolation && <><img className="sketch-evidence-full" src={assetUrl(selectedViolation.evidence_url)} alt="Minh chứng không đội mũ" /><p>Mã theo dõi: {selectedViolation.vehicle_id || '—'} · Khung hình: {selectedViolation.frame_number ?? 'Ảnh tĩnh'} · Thời điểm: {formatTimestamp(selectedViolation.timestamp_seconds)} · Độ tin cậy: {(selectedViolation.confidence * 100).toFixed(1)}%</p></>}
    </Modal>
  </div>
}

