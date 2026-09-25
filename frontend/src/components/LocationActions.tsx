import { useState } from 'react'
import { api } from '../services/api'
import type { Location, Project } from '../types'
import { PencilIcon, TrashIcon } from './Icons'
import { LocationModal } from './LocationModal'
import { Modal } from './Modal'

interface Props {
  location: Location
  projects: Project[]
  onSaved: () => void
  onDeleted: () => void
}

export function LocationActions({ location, projects, onSaved, onDeleted }: Props) {
  const [editing, setEditing] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState('')

  const remove = async () => {
    if (deleting) return
    setDeleting(true)
    setError('')
    try {
      await api.deleteLocation(location.id)
      setConfirming(false)
      onDeleted()
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Không thể xóa địa điểm.')
    } finally {
      setDeleting(false)
    }
  }

  return <>
    <button className="button button-outline" onClick={() => setEditing(true)} aria-label={`Sửa địa điểm ${location.name}`}><PencilIcon size={18} /> Sửa địa điểm</button>
    <button className="button button-ghost danger-text" onClick={() => { setError(''); setConfirming(true) }} aria-label={`Xóa địa điểm ${location.name}`}><TrashIcon size={18} /> Xóa địa điểm</button>
    <LocationModal open={editing} location={location} projects={projects} onClose={() => setEditing(false)} onCreated={onSaved} />
    <Modal open={confirming} title="Xóa địa điểm" size="small" onClose={() => { if (!deleting) setConfirming(false) }}>
      <p>Bạn có chắc muốn xóa địa điểm <strong>{location.name}</strong>? Toàn bộ phiên phân tích và dữ liệu vi phạm thuộc địa điểm sẽ bị xóa. Thao tác này không thể hoàn tác.</p>
      {error && <div className="alert alert-danger" role="alert">{error}</div>}
      <div className="form-actions">
        <button className="button button-ghost" disabled={deleting} onClick={() => setConfirming(false)}>Hủy</button>
        <button className="button button-outline danger-text" disabled={deleting} onClick={() => void remove()}>{deleting ? 'Đang xóa...' : 'Xóa địa điểm'}</button>
      </div>
    </Modal>
  </>
}
