import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { LocationActions } from '../components/LocationActions'
import { ArrowLeftIcon, DownloadIcon, EyeIcon, PinIcon, UploadIcon } from '../components/Icons'
import { ErrorPage, LoadingPage } from '../components/PageState'
import { StatCard } from '../components/StatCard'
import { StatusBadge } from '../components/StatusBadge'
import { UploadModal } from '../components/UploadModal'
import { api, assetUrl } from '../services/api'
import type { Analysis, Location, Project, Statistics, Violation } from '../types'
import { formatDate, formatPercent, formatTime, formatTimestamp } from '../utils'

export function LocationDetail() {
  const { locationId } = useParams()
  const navigate = useNavigate()
  const id = Number(locationId)
  const [location, setLocation] = useState<Location | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [stats, setStats] = useState<Statistics | null>(null)
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [violations, setViolations] = useState<Violation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [uploadModal, setUploadModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'history' | 'violations' | 'statistics'>('history')
  const [selectedViolation, setSelectedViolation] = useState<Violation | null>(null)

  const load = useCallback(async () => {
    if (!id) return
    setError('')
    try {
      const [locationRow, projectRows, statRow, analysisRows, violationRows] = await Promise.all([
        api.location(id),
        api.projects(),
        api.locationStatistics(id),
        api.analyses({ location_id: id, limit: 300 }),
        api.locationViolations(id, 300),
      ])
      setLocation(locationRow)
      setProjects(projectRows)
      setStats(statRow)
      setAnalyses(analysisRows)
      setViolations(violationRows)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Không thể tải địa điểm.')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { void load() }, [load])

  const project = useMemo(
    () => projects.find((item) => item.id === location?.project_id),
    [projects, location],
  )
  const maxTimeViolation = Math.max(1, ...(stats?.by_time_slot.map((item) => item.violations) || [1]))

  if (loading) return <LoadingPage text="Đang tải dữ liệu địa điểm..." />
  if (error || !location || !stats) return <ErrorPage message={error || 'Không tìm thấy địa điểm.'} onRetry={() => void load()} />

  return (
    <div className="detail-page page-enter">
      <div className="page-toolbar">
        <button className="back-link" onClick={() => navigate(-1)}><ArrowLeftIcon size={18} /> Quay lại</button>
        <div className="toolbar-actions">
          <LocationActions location={location} projects={projects} onSaved={() => void load()} onDeleted={() => navigate(`/projects/${location.project_id}`, { replace: true })} />
          <a className="button button-outline" href={api.downloadLocationUrl(id)}><DownloadIcon size={18} /> Tải dữ liệu</a>
          <button className="button button-primary" onClick={() => setUploadModal(true)}><UploadIcon size={18} /> Upload dữ liệu</button>
        </div>
      </div>

      <header className="detail-header">
        <div className="detail-icon pin"><PinIcon size={28} /></div>
        <div>
          <p className="eyebrow">{project?.name || location.project_name || 'Dự án'}</p>
          <h1>{location.name}</h1>
          <p>{location.description || 'Địa điểm giám sát ảnh/video giao thông.'}</p>
        </div>
      </header>

      <section className="stats-grid">
        <StatCard label="Tổng dữ liệu" value={stats.total_sessions} hint="Phiên đã hoàn thành" />
        <StatCard label="Tổng phương tiện" value={stats.total_vehicles.toLocaleString('vi-VN')} hint="Đã phát hiện/đếm" />
        <StatCard label="Tổng vi phạm" value={stats.total_violations.toLocaleString('vi-VN')} hint="Không đội mũ" tone="danger" />
        <StatCard label="Tỷ lệ vi phạm" value={formatPercent(stats.violation_rate)} hint={stats.peak_time_slot ? `Cao nhất ${stats.peak_time_slot.time_slot}` : 'Chưa đủ dữ liệu'} tone="warning" />
      </section>

      <div className="tabs" role="tablist">
        <button className={activeTab === 'history' ? 'active' : ''} onClick={() => setActiveTab('history')}>Dữ liệu đã phân tích <span>{analyses.length}</span></button>
        <button className={activeTab === 'violations' ? 'active' : ''} onClick={() => setActiveTab('violations')}>Ảnh vi phạm <span>{violations.length}</span></button>
        <button className={activeTab === 'statistics' ? 'active' : ''} onClick={() => setActiveTab('statistics')}>Thống kê khung giờ</button>
      </div>

      {activeTab === 'history' && (
        <section className="panel tab-panel">
          <div className="panel-heading"><div><p className="eyebrow">Lịch sử</p><h2>Phiên phân tích</h2></div></div>
          {analyses.length === 0 ? (
            <EmptyState title="Chưa có dữ liệu" description="Upload ảnh/video cho địa điểm này để tạo phiên phân tích đầu tiên." action={<button className="button button-primary" onClick={() => setUploadModal(true)}>Upload ngay</button>} />
          ) : (
            <div className="table-scroll"><table className="data-table"><thead><tr><th>Ngày</th><th>Khung giờ</th><th>File</th><th>Phương tiện</th><th>Đội mũ</th><th>Vi phạm</th><th>Tỷ lệ</th><th>Trạng thái</th><th /></tr></thead><tbody>
              {analyses.map((item) => (
                <tr key={item.id}>
                  <td>{formatDate(item.analysis_date)}</td>
                  <td>{formatTime(item.start_time)} – {formatTime(item.end_time)}</td>
                  <td>{item.total_files}</td>
                  <td>{item.total_vehicles}</td>
                  <td>{item.helmet_count}</td>
                  <td><span className="danger-number">{item.violation_count}</span></td>
                  <td>{formatPercent(item.violation_rate)}</td>
                  <td><StatusBadge status={item.status} /></td>
                  <td><Link className="row-link" to={`/analyses/${item.id}`}>Xem chi tiết</Link></td>
                </tr>
              ))}
            </tbody></table></div>
          )}
        </section>
      )}

      {activeTab === 'violations' && (
        <section className="panel tab-panel">
          <div className="panel-heading"><div><p className="eyebrow">Bằng chứng</p><h2>Trường hợp không đội mũ</h2></div><span className="muted">Click ảnh để xem thông tin</span></div>
          {violations.length === 0 ? (
            <EmptyState title="Chưa có ảnh vi phạm" description="Ảnh bằng chứng sẽ xuất hiện sau khi AI phát hiện trường hợp không đội mũ." />
          ) : (
            <div className="evidence-grid">
              {violations.map((item) => (
                <button className="evidence-card" key={item.id} onClick={() => setSelectedViolation(item)}>
                  <div className="evidence-image"><img src={assetUrl(item.evidence_url)} alt={`Vi phạm ${item.id}`} loading="lazy" /><span><EyeIcon size={18} /> Xem</span></div>
                  <div className="evidence-meta"><strong>{item.vehicle_id || `Vi phạm #${item.id}`}</strong><span>{formatTimestamp(item.timestamp_seconds)} · {(item.confidence * 100).toFixed(1)}%</span></div>
                </button>
              ))}
            </div>
          )}
        </section>
      )}

      {activeTab === 'statistics' && (
        <section className="panel tab-panel statistics-panel">
          <div className="panel-heading"><div><p className="eyebrow">Thống kê hỗ trợ</p><h2>Vi phạm theo khung giờ</h2></div></div>
          {stats.by_time_slot.length === 0 ? (
            <EmptyState title="Chưa đủ dữ liệu thống kê" description="Hoàn thành ít nhất một phiên phân tích để xem phân bố theo khung giờ." />
          ) : (
            <div className="bar-chart-list">
              {stats.by_time_slot.map((item) => (
                <div className="bar-row" key={item.time_slot}>
                  <span>{item.time_slot}</span>
                  <div className="bar-track"><div className="bar-value" style={{ width: `${Math.max(4, item.violations / maxTimeViolation * 100)}%` }} /></div>
                  <strong>{item.violations}</strong>
                </div>
              ))}
              {stats.peak_time_slot && <div className="peak-note">Khung giờ có nhiều vi phạm nhất: <strong>{stats.peak_time_slot.time_slot}</strong> ({stats.peak_time_slot.violations} trường hợp)</div>}
            </div>
          )}
        </section>
      )}

      {selectedViolation && (
        <div className="lightbox" onMouseDown={() => setSelectedViolation(null)} role="presentation">
          <div className="lightbox-panel" onMouseDown={(event) => event.stopPropagation()}>
            <button className="lightbox-close" onClick={() => setSelectedViolation(null)}>×</button>
            <img src={assetUrl(selectedViolation.evidence_url)} alt="Ảnh bằng chứng vi phạm" />
            <div className="lightbox-info">
              <h3>Không đội mũ bảo hiểm</h3>
              <p><span>Mã đối tượng</span><strong>{selectedViolation.vehicle_id || 'Không có'}</strong></p>
              <p><span>Thời gian video</span><strong>{formatTimestamp(selectedViolation.timestamp_seconds)}</strong></p>
              <p><span>Độ tin cậy</span><strong>{(selectedViolation.confidence * 100).toFixed(2)}%</strong></p>
              <p><span>File nguồn</span><strong>{selectedViolation.media_filename || `Media #${selectedViolation.media_id}`}</strong></p>
            </div>
          </div>
        </div>
      )}

      {project && (
        <UploadModal open={uploadModal} projects={[project]} initialProjectId={project.id} initialLocationId={id} onClose={() => setUploadModal(false)} onSubmitted={() => void load()} />
      )}
    </div>
  )
}
