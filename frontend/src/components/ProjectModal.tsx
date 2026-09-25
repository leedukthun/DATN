import { useEffect, useState, type FormEvent } from 'react'
import { api } from '../services/api'
import type { Project } from '../types'
import { Modal } from './Modal'

interface Props {
  open: boolean
  project?: Project | null
  onClose: () => void
  onSaved: (project: Project) => void
}

export function ProjectModal({ open, project, onClose, onSaved }: Props) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const isEdit = Boolean(project)

  useEffect(() => {
    if (!open) return
    setError('')
    setName(project?.name || '')
    setDescription(project?.description || '')
  }, [open, project])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    if (!name.trim()) {
      setError('Vui lòng nhập tên dự án.')
      return
    }
    setSaving(true)
    try {
      const payload = { name: name.trim(), description: description.trim() || undefined }
      const saved = project
        ? await api.updateProject(project.id, payload)
        : await api.createProject(payload)
      onSaved(saved)
      onClose()
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Không thể lưu dự án.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Đổi tên dự án' : 'Tạo dự án'}
      subtitle={isEdit ? 'Cập nhật tên và mô tả dự án.' : 'Mỗi dự án có thể quản lý nhiều địa điểm.'}
      size="small"
    >
      <form className="form-stack" onSubmit={submit}>
        <label>
          <span>Tên dự án *</span>
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Ví dụ: Theo dõi khu vực Nguyễn Trãi" autoFocus />
        </label>
        <label>
          <span>Mô tả</span>
          <textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Mục tiêu hoặc phạm vi dự án" rows={4} />
        </label>
        {error && <div className="alert alert-danger">{error}</div>}
        <div className="form-actions">
          <button type="button" className="button button-ghost" onClick={onClose}>Hủy</button>
          <button type="submit" className="button button-primary" disabled={saving}>
            {saving ? 'Đang lưu...' : isEdit ? 'Lưu thay đổi' : 'Tạo dự án'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
