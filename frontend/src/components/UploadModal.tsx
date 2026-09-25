import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import type { Analysis, Project } from '../types'
import { fileSize, todayIso } from '../utils'
import { CloseIcon, ImageIcon, UploadIcon, VideoIcon } from './Icons'
import { Modal } from './Modal'

interface Props {
  open: boolean
  projects: Project[]
  initialProjectId?: number | null
  initialLocationId?: number | null
  initialFiles?: File[]
  onClose: () => void
  onSubmitted?: () => void
  inline?: boolean
  onAnalysisCreated?: (analysis: Analysis) => void
}

const allowed = ['jpg', 'jpeg', 'png', 'bmp', 'webp', 'mp4', 'avi', 'mov', 'mkv', 'webm', 'm4v']

function uniqueFiles(files: File[]): File[] {
  const map = new Map<string, File>()
  files.forEach((file) => map.set(`${file.name}-${file.size}-${file.lastModified}`, file))
  return Array.from(map.values())
}

export function UploadModal({
  open,
  projects,
  initialProjectId,
  initialLocationId,
  initialFiles,
  onClose,
  onSubmitted,
  inline = false,
  onAnalysisCreated,
}: Props) {
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  const [projectId, setProjectId] = useState<number | ''>('')
  const [locationId, setLocationId] = useState<number | ''>('')
  const [analysisDate, setAnalysisDate] = useState(todayIso())
  const [startTime, setStartTime] = useState('07:00')
  const [endTime, setEndTime] = useState('08:00')
  const [files, setFiles] = useState<File[]>([])
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === Number(projectId)),
    [projectId, projects],
  )
  const locations = selectedProject?.locations || []

  useEffect(() => {
    if (!open) return
    const nextProject = initialProjectId || projects[0]?.id || ''
    setProjectId(nextProject)
    const project = projects.find((item) => item.id === Number(nextProject))
    const locationExists = project?.locations.some((item) => item.id === initialLocationId)
    setLocationId(locationExists ? initialLocationId || '' : project?.locations[0]?.id || '')
    setFiles(initialFiles || [])
    setError('')
  }, [open, initialProjectId, initialLocationId, initialFiles, projects])

  useEffect(() => {
    if (!projectId) {
      setLocationId('')
      return
    }
    if (!locations.some((item) => item.id === Number(locationId))) {
      setLocationId(locations[0]?.id || '')
    }
  }, [projectId, locationId, locations])

  const addFiles = (incoming: File[]) => {
    if (submitting) return
    const invalid = incoming.filter((file) => !allowed.includes(file.name.split('.').pop()?.toLowerCase() || ''))
    if (invalid.length) {
      setError(`Định dạng không hỗ trợ: ${invalid.map((file) => file.name).join(', ')}`)
    } else {
      setError('')
    }
    setFiles((current) => uniqueFiles([...current, ...incoming.filter((file) => !invalid.includes(file))]))
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    if (!projectId || !locationId) {
      setError('Vui lòng tạo/chọn dự án và địa điểm trước khi upload.')
      return
    }
    if (!files.length) {
      setError('Vui lòng chọn ít nhất một ảnh hoặc video.')
      return
    }
    if (startTime >= endTime) {
      setError('Giờ kết thúc phải sau giờ bắt đầu.')
      return
    }

    const body = new FormData()
    body.append('project_id', String(projectId))
    body.append('location_id', String(locationId))
    body.append('analysis_date', analysisDate)
    body.append('start_time', startTime)
    body.append('end_time', endTime)
    files.forEach((file) => body.append('files', file))

    setSubmitting(true)
    try {
      const analysis = await api.createAnalysis(body)
      if (onAnalysisCreated) {
        onAnalysisCreated(analysis)
        return
      }
      onSubmitted?.()
      onClose()
      navigate(`/analyses/${analysis.id}`)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Không thể tạo phiên phân tích.')
    } finally {
      setSubmitting(false)
    }
  }

  const form = (
      <form className="upload-form" onSubmit={submit}>
        <div className="form-grid form-grid-2">
          <label>
            <span>Dự án *</span>
            <select value={projectId} onChange={(event) => setProjectId(Number(event.target.value) || '')} disabled={submitting}>
              <option value="">Chọn dự án</option>
              {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
            </select>
          </label>
          <label>
            <span>Địa điểm *</span>
            <select value={locationId} onChange={(event) => setLocationId(Number(event.target.value) || '')} disabled={submitting || !projectId}>
              <option value="">Chọn địa điểm</option>
              {locations.map((location) => <option key={location.id} value={location.id}>{location.name}</option>)}
            </select>
            {projectId && !locations.length && <small>Dự án này chưa có địa điểm.</small>}
          </label>
          <label>
            <span>Ngày khảo sát *</span>
            <input required type="date" value={analysisDate} onChange={(event) => setAnalysisDate(event.target.value)} disabled={submitting} />
          </label>
          <div className="time-range">
            <label>
              <span>Bắt đầu *</span>
              <input type="time" value={startTime} onChange={(event) => setStartTime(event.target.value)} disabled={submitting} />
            </label>
            <span className="time-separator">→</span>
            <label>
              <span>Kết thúc *</span>
              <input type="time" value={endTime} onChange={(event) => setEndTime(event.target.value)} disabled={submitting} />
            </label>
          </div>
        </div>

        <div
          className={`modal-dropzone ${dragging ? 'is-dragging' : ''}`}
          onDragOver={(event) => {
            event.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(event) => {
            event.preventDefault()
            setDragging(false)
            addFiles(Array.from(event.dataTransfer.files))
          }}
          onClick={() => !submitting && inputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(event) => !submitting && event.key === 'Enter' && inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            disabled={submitting}
            multiple
            accept="image/*,video/*"
            hidden
            onChange={(event) => addFiles(Array.from(event.target.files || []))}
          />
          <div className="dropzone-icon"><UploadIcon size={32} /></div>
          <strong>Kéo thả ảnh/video vào đây</strong>
          <span className="button button-outline">Chọn tệp</span>
          <small>Ảnh: JPG, PNG, WEBP… · Video: MP4, AVI, MOV, MKV…</small>
        </div>

        <div className="selected-files">
          <div className="selected-files-header">
            <strong>Đã chọn {files.length} file</strong>
            {files.length > 0 && (
              <button type="button" className="text-button danger-text" onClick={() => setFiles([])} disabled={submitting}>Xóa tất cả</button>
            )}
          </div>
          {files.length === 0 ? (
            <p className="muted">Chưa có file nào được chọn.</p>
          ) : (
            <div className="file-list">
              {files.map((file, index) => {
                const video = file.type.startsWith('video/')
                return (
                  <div className="file-row" key={`${file.name}-${file.lastModified}`}>
                    <span className="file-type-icon">{video ? <VideoIcon /> : <ImageIcon />}</span>
                    <div className="file-meta">
                      <strong>{file.name}</strong>
                      <span>{fileSize(file.size)}</span>
                    </div>
                    <button
                      type="button"
                      className="icon-button small"
                      aria-label={`Xóa ${file.name}`}
                      onClick={() => setFiles((current) => current.filter((_, currentIndex) => currentIndex !== index))}
                      disabled={submitting}
                    >
                      <CloseIcon size={17} />
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {error && <div className="alert alert-danger">{error}</div>}
        <div className="form-actions sticky-actions">
          {!inline && <button type="button" className="button button-ghost" onClick={onClose} disabled={submitting}>Hủy</button>}
          <button type="submit" className="button button-primary button-wide" disabled={submitting || !files.length}>
            <UploadIcon size={19} />
            {submitting ? 'Đang tải dữ liệu...' : 'Bắt đầu phân tích'}
          </button>
        </div>
      </form>
  )
  return inline ? form : <Modal open={open} onClose={() => !submitting && onClose()} title="Thông tin dữ liệu" subtitle="Gắn file với dự án, địa điểm, ngày và khung giờ trước khi phân tích." size="large">{form}</Modal>
}
