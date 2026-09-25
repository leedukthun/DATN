import { useEffect, type ReactNode } from 'react'
import { CloseIcon } from './Icons'

interface ModalProps {
  open: boolean
  title: string
  subtitle?: string
  onClose: () => void
  children: ReactNode
  size?: 'small' | 'medium' | 'large'
}

export function Modal({ open, title, subtitle, onClose, children, size = 'medium' }: ModalProps) {
  useEffect(() => {
    if (!open) return
    const listener = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', listener)
    return () => {
      window.removeEventListener('keydown', listener)
    }
  }, [open, onClose])

  if (!open) return null
  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <section
        className={`modal-panel modal-${size}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <div>
            <h2>{title}</h2>
            {subtitle && <p>{subtitle}</p>}
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Đóng">
            <CloseIcon />
          </button>
        </header>
        <div className="modal-body">{children}</div>
      </section>
    </div>
  )
}
