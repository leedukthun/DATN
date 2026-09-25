import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { ArrowLeftIcon, ChartIcon, DownloadIcon, PencilIcon, PinIcon, PlusIcon, TrashIcon, UploadIcon } from '../components/Icons'
import { LocationModal } from '../components/LocationModal'
import { LocationActions } from '../components/LocationActions'
import { ProjectModal } from '../components/ProjectModal'
import { ErrorPage, LoadingPage } from '../components/PageState'
import { StatCard } from '../components/StatCard'
import { StatusBadge } from '../components/StatusBadge'
import { UploadModal } from '../components/UploadModal'
import { api } from '../services/api'
import type { Analysis, Project, Statistics } from '../types'
import { formatDate, formatPercent, formatTime } from '../utils'

export function ProjectDetail() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const id = Number(projectId)
  const [project, setProject] = useState<Project | null>(null)
  const [stats, setStats] = useState<Statistics | null>(null)
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [locationModal, setLocationModal] = useState(false)
  const [projectModal, setProjectModal] = useState(false)
  const [uploadModal, setUploadModal] = useState(false)
  const [uploadLocationId, setUploadLocationId] = useState<number | null>(null)

  const load = useCallback(async () => {
    if (!id) return
    setError('')
    try {
      const [projectRow, statRow, analysisRows] = await Promise.all([
        api.project(id),
        api.projectStatistics(id),
        api.analyses({ project_id: id, limit: 200 }),
      ])
      setProject(projectRow)
      setStats(statRow)
      setAnalyses(analysisRows)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Không thể tải dự án.')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { void load() }, [load])

  if (loading) return <LoadingPage text="Đang tải dự án..." />
  if (error || !project || !stats) return <ErrorPage message={error || 'Không tìm thấy dự án.'} onRetry={() => void load()} />

  return (
    <div className="detail-page page-enter">
      <div className="page-toolbar">
        <button className="back-link" onClick={() => navigate(-1)}><ArrowLeftIcon size={18} /> Quay lại</button>
        <div className="toolbar-actions">
          <button className="button button-outline" onClick={() => setProjectModal(true)}><PencilIcon size={18} /> Đổi tên</button>
          <button
            className="button button-ghost danger-text"
            onClick={async () => {
              const confirmed = window.confirm(`Xóa dự án "${project.name}"? Toàn bộ địa điểm và dữ liệu liên quan sẽ bị xóa.`)
              if (!confirmed) return
              try {
                await api.deleteProject(id)
                navigate('/', { replace: true })
              } catch (cause) {
                setError(cause instanceof Error ? cause.message : 'Không thể xóa dự án.')
              }
            }}
          >
            <TrashIcon size={18} /> Xóa dự án
          </button>
          <a className="button button-outline" href={api.downloadProjectUrl(id)}><DownloadIcon size={18} /> Tải dữ liệu</a>
          <button className="button button-primary" onClick={() => setUploadModal(true)} disabled={!project.locations.length}><UploadIcon size={18} /> Upload</button>
        </div>
      </div>

      <header className="detail-header">
        <div className="detail-icon"><ChartIcon size={28} /></div>
        <div><p className="eyebrow">Dự án</p><h1>{project.name}</h1><p>{project.description || 'Chưa có mô tả cho dự án này.'}</p></div>
      </header>

      <section className="stats-grid">
        <StatCard label="Địa điểm" value={project.locations.length} hint="Được quản lý trong dự án" />
        <StatCard label="Tổng phương tiện" value={stats.total_vehicles.toLocaleString('vi-VN')} hint={`${stats.total_sessions} phiên hoàn thành`} />
        <StatCard label="Tổng vi phạm" value={stats.total_violations.toLocaleString('vi-VN')} hint="Không đội mũ" tone="danger" />
        <StatCard label="Tỷ lệ vi phạm" value={formatPercent(stats.violation_rate)} hint={stats.peak_time_slot ? `Cao nhất: ${stats.peak_time_slot.time_slot}` : 'Chưa đủ dữ liệu'} tone="warning" />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div><p className="eyebrow">Cấu trúc dự án</p><h2>Địa điểm</h2></div>
          <button className="button button-soft button-small" onClick={() => setLocationModal(true)}><PlusIcon size={17} /> Thêm địa điểm</button>
        </div>
        {project.locations.length === 0 ? (
          <EmptyState title="Dự án chưa có địa điểm" description="Thêm một địa điểm để gắn dữ liệu ảnh/video với vị trí quan sát." action={<button className="button button-primary" onClick={() => setLocationModal(true)}>Thêm địa điểm</button>} />
        ) : (
          <div className="location-card-grid">
            {project.locations.map((location) => {
              const locationAnalyses = analyses.filter((item) => item.location_id === location.id)
              const violations = locationAnalyses.reduce((sum, item) => sum + item.violation_count, 0)
              return (
                <article className="location-card" key={location.id}>
                  <div className="location-card-top"><span><PinIcon /></span><small>{locationAnalyses.length} phiên</small></div>
                  <h3>{location.name}</h3>
                  <p>{location.description || 'Chưa có mô tả địa điểm.'}</p>
                  <div className="location-mini-stats"><span><strong>{violations}</strong> vi phạm</span><span><strong>{locationAnalyses.reduce((sum, item) => sum + item.total_vehicles, 0)}</strong> đối tượng</span></div>
                  <div className="card-actions"><Link className="button button-soft" to={`/locations/${location.id}`}>Xem chi tiết</Link><button className="button button-ghost" onClick={() => { setUploadLocationId(location.id); setUploadModal(true) }}>Upload</button></div>
                  <div className="card-actions location-management-actions"><LocationActions location={location} projects={[project]} onSaved={() => void load()} onDeleted={() => { setUploadLocationId(null); void load() }} /></div>
                </article>
              )
            })}
          </div>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading"><div><p className="eyebrow">Lịch sử</p><h2>Phiên phân tích</h2></div><span className="muted">{analyses.length} phiên</span></div>
        {analyses.length === 0 ? <EmptyState title="Chưa có dữ liệu" description="Upload ảnh hoặc video vào một địa điểm trong dự án." /> : (
          <div className="table-scroll"><table className="data-table"><thead><tr><th>Ngày</th><th>Địa điểm</th><th>Khung giờ</th><th>Phương tiện</th><th>Vi phạm</th><th>Tỷ lệ</th><th>Trạng thái</th><th /></tr></thead><tbody>
            {analyses.map((item) => <tr key={item.id}><td>{formatDate(item.analysis_date)}</td><td><strong>{item.location_name}</strong></td><td>{formatTime(item.start_time)} – {formatTime(item.end_time)}</td><td>{item.total_vehicles}</td><td><span className="danger-number">{item.violation_count}</span></td><td>{formatPercent(item.violation_rate)}</td><td><StatusBadge status={item.status} /></td><td><Link className="row-link" to={`/analyses/${item.id}`}>Chi tiết</Link></td></tr>)}
          </tbody></table></div>
        )}
      </section>

      <LocationModal open={locationModal} projects={[project]} initialProjectId={project.id} onClose={() => setLocationModal(false)} onCreated={() => void load()} />
      <ProjectModal open={projectModal} project={project} onClose={() => setProjectModal(false)} onSaved={() => void load()} />
      <UploadModal open={uploadModal} projects={[project]} initialProjectId={project.id} initialLocationId={uploadLocationId || project.locations[0]?.id} onClose={() => setUploadModal(false)} onSubmitted={() => void load()} />
    </div>
  )
}
