import { useCallback, useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { LocationActions } from '../components/LocationActions'
import { LocationModal } from '../components/LocationModal'
import { ProjectModal } from '../components/ProjectModal'
import { LoadingPage } from '../components/PageState'
import { ShieldIcon } from '../components/Icons'
import { api } from '../services/api'
import type { Analysis, Project } from '../types'

export function Dashboard() {
  const [params, setParams] = useSearchParams()
  const [projects, setProjects] = useState<Project[]>([])
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [projectModal, setProjectModal] = useState(false)
  const [editing, setEditing] = useState<Project | null>(null)
  const [locationModal, setLocationModal] = useState(false)
  const [deleting, setDeleting] = useState<number | null>(null)
  const selected = projects.find(p => p.id === Number(params.get('project'))) || projects[0]
  const load = useCallback(async () => {
    try {
      const [projectRows, analysisRows] = await Promise.all([api.projects(), api.allAnalyses()])
      setProjects(projectRows); setAnalyses(analysisRows); setError('')
    }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Không thể tải dự án.') }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { void load() }, [load])
  const remove = async (project: Project) => {
    if (!window.confirm(`Xóa dự án "${project.name}" và toàn bộ địa điểm, phiên phân tích liên quan? Thao tác không thể hoàn tác.`)) return
    setDeleting(project.id)
    try { await api.deleteProject(project.id); await load() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Không thể xóa dự án.') }
    finally { setDeleting(null) }
  }
  if (loading) return <LoadingPage text="Đang tải dự án..." />
  return <div className="sketch-page">
    <section className="hero-section" aria-labelledby="hero-title">
      <div className="hero-copy">
        <p className="eyebrow">Computer Vision </p>
        <h1 id="hero-title">Phát hiện người điều khiển xe máy <span>không đội mũ bảo hiểm</span></h1>
        <p>Hệ thống tự động phân tích và thống kê</p>
      </div>
      <div className="hero-visual" aria-hidden="true">
        <div className="camera-frame">
          <span className="corner corner-a" />
          <span className="corner corner-b" />
          <span className="corner corner-c" />
          <span className="corner corner-d" />
          <div className="helmet-orbit"><ShieldIcon size={64} /></div>
          <div className="detect-box box-one"><span>NO HELMET</span></div>
          <div className="detect-box box-two"><span>HELMET</span></div>
          <div className="scan-line" />
        </div>
      </div>
    </section>
    <div className="sketch-title"><h1>Dự án và địa điểm</h1><button className="button button-primary" onClick={() => { setEditing(null); setProjectModal(true) }}>+ Tạo dự án</button></div>
    {error && <div className="alert alert-danger" role="alert">{error}<button className="text-button" onClick={() => void load()}>Thử lại</button></div>}
    <div className="sketch-columns project-columns">
      <section className="panel"><h2>Danh sách dự án</h2>
        {!projects.length && <p className="muted">Chưa có dự án. Tạo dự án để bắt đầu quản lý địa điểm.</p>}
        {projects.map(project => <article key={project.id} className={`sketch-list-row ${selected?.id === project.id ? 'selected' : ''}`}>
          <div className="sketch-row-heading"><h3>{project.name}</h3>{selected?.id === project.id ? <span className="muted">Đang chọn</span> : <button className="button button-outline" onClick={() => setParams({ project: String(project.id) })}>Mở</button>}</div>
          <p className="muted">{project.description || 'Chưa có mô tả dự án.'}</p>
          {selected?.id === project.id && <div className="sketch-actions"><button className="button button-outline" onClick={() => { setEditing(project); setProjectModal(true) }}>Chỉnh sửa</button><button className="button button-outline" disabled={deleting !== null} onClick={() => void remove(project)}>{deleting === project.id ? 'Đang xóa...' : 'Xóa'}</button></div>}
        </article>)}
      </section>
      <section className="panel"><div className="panel-heading"><h2>{selected ? `Địa điểm thuộc ${selected.name}` : 'Địa điểm thuộc dự án'}</h2><button className="button button-outline" disabled={!selected} onClick={() => setLocationModal(true)}>+ Thêm địa điểm</button></div>
        {!selected?.locations.length && <p className="muted">{selected ? 'Chưa có địa điểm. Thêm địa điểm để gắn dữ liệu quan sát.' : 'Chọn hoặc tạo một dự án.'}</p>}
        {selected?.locations.map(location => <article className="sketch-list-row" key={location.id}>
          <div className="sketch-row-heading"><h3>{location.name}</h3><Link className="button button-outline" to={`/locations/${location.id}`}>Xem</Link></div>
          <p className="muted">{location.description || 'Chưa có mô tả địa điểm.'} · Số phiên: {analyses.filter(a => a.location_id === location.id).length}</p>
          <div className="sketch-actions"><LocationActions location={location} projects={projects} onSaved={() => void load()} onDeleted={() => void load()} /></div>
        </article>)}
      </section>
    </div>
    <ProjectModal open={projectModal} project={editing} onClose={() => setProjectModal(false)} onSaved={project => { setParams({ project: String(project.id) }); void load() }} />
    <LocationModal open={locationModal} projects={projects} initialProjectId={selected?.id} onClose={() => setLocationModal(false)} onCreated={() => void load()} />
  </div>
}
