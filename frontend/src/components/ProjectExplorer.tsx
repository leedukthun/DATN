import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import type { Project } from '../types'
import { ChartIcon, ChevronIcon, DownloadIcon, FolderIcon, PencilIcon, PinIcon, PlusIcon, TrashIcon } from './Icons'

interface Props {
  projects: Project[]
  onCreateProject: () => void
  onEditProject: (project: Project) => void
  onDeleteProject: (project: Project) => void
  onCreateLocation: (projectId: number) => void
  onUpload: (projectId?: number, locationId?: number) => void
}

export function ProjectExplorer({
  projects,
  onCreateProject,
  onEditProject,
  onDeleteProject,
  onCreateLocation,
  onUpload,
}: Props) {
  const [expanded, setExpanded] = useState<Set<number>>(() => new Set(projects.slice(0, 1).map((item) => item.id)))

  const toggle = (id: number) => {
    setExpanded((current) => {
      const next = new Set(current)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <section className="project-explorer panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Không gian lưu trữ</p>
          <h2>Dự án</h2>
        </div>
        <button className="button button-soft button-small" onClick={onCreateProject}><PlusIcon size={17} /> Dự án</button>
      </div>

      {projects.length === 0 ? (
        <div className="mini-empty">
          <FolderIcon size={34} />
          <strong>Chưa có dự án</strong>
          <span>Tạo dự án đầu tiên để thêm địa điểm và dữ liệu.</span>
          <button className="button button-primary button-small" onClick={onCreateProject}>Tạo dự án</button>
        </div>
      ) : (
        <div className="project-tree">
          {projects.map((project) => {
            const isOpen = expanded.has(project.id)
            return (
              <article className="project-node" key={project.id}>
                <div className="project-node-title">
                  <button className={`tree-toggle ${isOpen ? 'open' : ''}`} onClick={() => toggle(project.id)} aria-label={isOpen ? 'Thu gọn' : 'Mở rộng'}>
                    <ChevronIcon size={17} />
                  </button>
                  <Link to={`/projects/${project.id}`} className="project-name-link">
                    <span className="project-icon"><FolderIcon size={18} /></span>
                    <span>
                      <strong>{project.name}</strong>
                      <small>{project.locations.length} địa điểm</small>
                    </span>
                  </Link>
                  <div className="project-node-actions">
                    <button className="icon-button small" title="Đổi tên dự án" onClick={() => onEditProject(project)}><PencilIcon size={15} /></button>
                    <button className="icon-button small danger" title="Xóa dự án" onClick={() => onDeleteProject(project)}><TrashIcon size={15} /></button>
                    <button className="icon-button small" title="Thêm địa điểm" onClick={() => onCreateLocation(project.id)}><PlusIcon size={17} /></button>
                  </div>
                </div>

                {isOpen && (
                  <div className="location-tree">
                    {project.locations.length === 0 ? (
                      <button className="add-location-row" onClick={() => onCreateLocation(project.id)}><PlusIcon size={15} /> Thêm địa điểm</button>
                    ) : (
                      project.locations.map((location) => (
                        <div className="location-row" key={location.id}>
                          <Link to={`/locations/${location.id}`} className="location-link">
                            <PinIcon size={16} />
                            <span>{location.name}</span>
                          </Link>
                          <div className="location-actions">
                            <button title="Upload dữ liệu" onClick={() => onUpload(project.id, location.id)}>Upload</button>
                            <Link title="Dữ liệu và thống kê" to={`/locations/${location.id}`}><ChartIcon size={15} /></Link>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}

                <div className="project-footer-actions">
                  <button onClick={() => onUpload(project.id, project.locations[0]?.id)} disabled={!project.locations.length}>Upload ảnh/video</button>
                  <a href={api.downloadProjectUrl(project.id)}><DownloadIcon size={15} /> Tải dữ liệu</a>
                </div>
              </article>
            )
          })}
        </div>
      )}
    </section>
  )
}
