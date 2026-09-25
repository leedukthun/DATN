import { useEffect, useState, type FormEvent } from 'react'
import { api } from '../services/api'
import type { Location, Project } from '../types'
import { Modal } from './Modal'

interface Props {
  open: boolean
  projects: Project[]
  initialProjectId?: number | null
  location?: Location | null
  onClose: () => void
  onCreated: (location: Location) => void
}

export function LocationModal({ open, projects, initialProjectId, location, onClose, onCreated }: Props) {
  const [projectId, setProjectId] = useState<number | ''>('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!open) return
    setProjectId(location?.project_id || initialProjectId || projects[0]?.id || '')
    setName(location?.name || '')
    setDescription(location?.description || '')
    setError('')
  }, [open, initialProjectId, location])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    if (!projectId || !name.trim()) {
      setError('Vui lòng chọn dự án và nhập tên địa điểm.')
      return
    }
    setSaving(true)
    try {
      const payload = {
        name: name.trim(),
        description: description.trim(),
      }
      const saved = location
        ? await api.updateLocation(location.id, payload)
        : await api.createLocation(projectId, payload)
      onCreated(saved)
      setName('')
      setDescription('')
      onClose()
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Không thể lưu địa điểm.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={() => { if (!saving) onClose() }} title={location ? 'Sửa địa điểm' : 'Thêm địa điểm'} subtitle="Nhập tên và mô tả vị trí quan sát." size="small">
      <form className="form-stack" onSubmit={submit}>
        <label>
          <span>Dự án *</span>
          <select disabled={Boolean(location) || saving} value={projectId} onChange={(event) => setProjectId(Number(event.target.value) || '')}>
            <option value="">Chọn dự án</option>
            {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
          </select>
        </label>
        <label>
          <span>Tên địa điểm *</span>
          <input required maxLength={255} disabled={saving} value={name} onChange={(event) => setName(event.target.value)} placeholder="Ví dụ: Ngã tư Nguyễn Trãi - Khuất Duy Tiến" autoFocus />
        </label>
        <label>
          <span>Mô tả</span>
          <textarea maxLength={4000} disabled={saving} value={description} onChange={(event) => setDescription(event.target.value)} rows={3} placeholder="Vị trí camera, hướng quan sát..." />
        </label>
        {error && <div className="alert alert-danger">{error}</div>}
        <div className="form-actions">
          <button type="button" className="button button-ghost" disabled={saving} onClick={onClose}>Hủy</button>
          <button type="submit" className="button button-primary" disabled={saving}>{saving ? 'Đang lưu...' : location ? 'Lưu thay đổi' : 'Thêm địa điểm'}</button>
        </div>
      </form>
    </Modal>
  )
}
