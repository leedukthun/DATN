import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { StatCard } from '../components/StatCard'
import { StatusBadge } from '../components/StatusBadge'
import type { Analysis, Project } from '../types'
import { formatDate, formatPercent, formatTime } from '../utils'

export function StatisticsPage({ results = false }: { results?: boolean }) {
  const [projects, setProjects] = useState<Project[]>([])
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [projectId, setProjectId] = useState('')
  const [locationId, setLocationId] = useState('')
  const [date, setDate] = useState('')
  const [scope, setScope] = useState('location')
  const [sessionId, setSessionId] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [reload, setReload] = useState(0)
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    Promise.all([api.projects(), api.allAnalyses()]).then(([p, a]) => {
      if (cancelled) return
      setProjects(p); setAnalyses(a); setError('')
    }).catch(e => { if (!cancelled) setError(e.message) }).finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [reload])
  const project = projects.find(p => p.id === Number(projectId))
  const locations = project?.locations || []
  const filtered = analyses.filter(a => (!projectId || a.project_id === Number(projectId)) && (!locationId || a.location_id === Number(locationId)) && (!date || a.analysis_date === date))
  const completed = filtered.filter(a => a.status === 'COMPLETED')
  const total = completed.reduce((s, a) => s + a.total_vehicles, 0)
  const helmet = completed.reduce((s, a) => s + a.helmet_count, 0)
  const noHelmet = completed.reduce((s, a) => s + a.no_helmet_count, 0)
  const groups = new Map<string, { helmet: number; noHelmet: number }>()
  completed.forEach(a => {
    const key = `${formatTime(a.start_time)}–${formatTime(a.end_time)}`
    const group = groups.get(key) || { helmet: 0, noHelmet: 0 }
    group.helmet += a.helmet_count; group.noHelmet += a.no_helmet_count
    groups.set(key, group)
  })
  const slots = [...groups].sort(([a], [b]) => a.localeCompare(b))
  const maximum = Math.max(1, ...slots.flatMap(([, v]) => [v.helmet, v.noHelmet]))
  const peak = [...slots].sort((a, b) => b[1].noHelmet - a[1].noHelmet)[0]
  const selectedSession = filtered.find(a => a.id === Number(sessionId)) || filtered[0]
  const download = scope === 'project' ? (projectId ? api.downloadProjectUrl(Number(projectId)) : '') : scope === 'session' ? (selectedSession ? api.downloadAnalysisUrl(selectedSession.id) : '') : (locationId ? api.downloadLocationUrl(Number(locationId)) : '')
  return <div className="sketch-page">
    <div className="sketch-title"><h1>{results ? 'Kết quả nhận diện' : 'Thống kê dữ liệu'}</h1><span className="muted">{project?.name || 'Tất cả dự án'}{locationId ? ` / ${locations.find(l => l.id === Number(locationId))?.name || ''}` : ''}</span></div>
    <div className="sketch-filters">
      <label><span>Dự án</span><select value={projectId} onChange={e => { setProjectId(e.target.value); setLocationId('') }}><option value="">Tất cả dự án</option>{projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}</select></label>
      <label><span>Địa điểm</span><select value={locationId} disabled={!projectId} onChange={e => setLocationId(e.target.value)}><option value="">Tất cả địa điểm</option>{locations.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}</select></label>
      <label><span>Ngày khảo sát</span><input type="date" value={date} onChange={e => setDate(e.target.value)} /></label>
    </div>
    {error && <div className="alert alert-danger" role="alert">{error}<button className="text-button" onClick={() => setReload(v => v + 1)}>Thử lại</button></div>}
    {loading ? <p>Đang tải dữ liệu...</p> : !error && <>
      {!results && <>
        <section className="stats-grid"><StatCard label="Tổng đối tượng" value={total} /><StatCard label="Có mũ" tone="success" value={helmet} /><StatCard label="Không mũ" tone="danger" value={noHelmet} /><StatCard label="Tỷ lệ không mũ" tone="warning" value={formatPercent(total ? noHelmet / total * 100 : 0)} /></section>
        <section className="sketch-chart" aria-label="Biểu đồ có mũ và không mũ theo khung giờ">
          <h2>Số đối tượng có mũ / không mũ theo thời gian</h2>
          <div className="chart-legend"><span><i className="helmet-key" />Có mũ</span><span><i className="no-helmet-key" />Không mũ</span></div>
          {slots.length ? <div className="sketch-bars">{slots.map(([slot, values]) => <div className="sketch-bar-row" key={slot}><span>{slot}</span><div><div className="sketch-bar helmet-bar" style={{ width: `${Math.max(1, values.helmet / maximum * 100)}%` }}>{values.helmet}</div><div className="sketch-bar no-helmet-bar" style={{ width: `${Math.max(1, values.noHelmet / maximum * 100)}%` }}>{values.noHelmet}</div></div></div>)}</div> : <p>Chưa có phiên hoàn thành trong phạm vi đã chọn.</p>}
          <p>Khoảng thời gian ghi nhận không mũ nhiều nhất: <strong>{peak && peak[1].noHelmet > 0 ? `${peak[0]} (${peak[1].noHelmet})` : '—'}</strong></p>
        </section>
      </>}
      <div className="table-scroll"><table className="data-table sketch-table"><thead><tr><th>Phiên phân tích</th><th>Thời gian</th><th>Tổng đối tượng</th><th>Không mũ</th><th>Trạng thái</th><th>Kết quả</th></tr></thead><tbody>
        {filtered.map(a => <tr key={a.id}><td><strong>Phiên {a.id}</strong><small>{a.project_name} / {a.location_name}</small></td><td>{formatDate(a.analysis_date)}<small>{formatTime(a.start_time)}–{formatTime(a.end_time)}</small></td><td>{a.total_vehicles}</td><td>{a.no_helmet_count}</td><td><StatusBadge status={a.status} /></td><td><Link className="row-link" to={`/analyses/${a.id}`}>Xem</Link></td></tr>)}
        {!filtered.length && <tr><td colSpan={6}>Không có phiên phân tích phù hợp.</td></tr>}
      </tbody></table></div>
      {!results && <section className="sketch-download">
        <label><span>Phạm vi tải kết quả</span><select value={scope} onChange={e => setScope(e.target.value)}><option value="location">Địa điểm đang chọn</option><option value="project">Dự án đang chọn</option><option value="session">Một phiên phân tích</option></select></label>
        {scope === 'session' && <label><span>Phiên phân tích</span><select value={selectedSession?.id || ''} onChange={e => setSessionId(e.target.value)}><option value="" disabled>Chọn phiên</option>{filtered.map(a => <option key={a.id} value={a.id}>Phiên {a.id} · {formatDate(a.analysis_date)}</option>)}</select></label>}
        {download ? <a className="button button-primary" href={download}>Tải kết quả ZIP</a> : <button className="button button-primary" disabled>Tải kết quả ZIP</button>}
        <p className="muted">{!download ? 'Chọn dự án, địa điểm hoặc phiên tương ứng để tải kết quả. ' : ''}ZIP dự án/địa điểm chứa toàn bộ dữ liệu trong phạm vi đó, không giới hạn theo bộ lọc ngày. Thống kê chỉ tính phiên đã hoàn thành.</p>
      </section>}
    </>}
  </div>
}

