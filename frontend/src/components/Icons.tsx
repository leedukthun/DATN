import type { ReactNode, SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement> & { size?: number }

const Base = ({ size = 20, children, ...props }: IconProps & { children: ReactNode }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    {children}
  </svg>
)

export const UploadIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M12 16V4" />
    <path d="m7 9 5-5 5 5" />
    <path d="M5 20h14" />
  </Base>
)

export const FolderIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M3 6.5h6l2 2h10v9.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
  </Base>
)

export const PinIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" />
    <circle cx="12" cy="10" r="2.5" />
  </Base>
)

export const ChartIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M4 20V10" />
    <path d="M10 20V4" />
    <path d="M16 20v-7" />
    <path d="M22 20H2" />
  </Base>
)

export const DownloadIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M12 3v12" />
    <path d="m7 10 5 5 5-5" />
    <path d="M5 21h14" />
  </Base>
)

export const PlusIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M12 5v14" />
    <path d="M5 12h14" />
  </Base>
)

export const ImageIcon = (props: IconProps) => (
  <Base {...props}>
    <rect x="3" y="4" width="18" height="16" rx="2" />
    <circle cx="8.5" cy="9" r="1.5" />
    <path d="m21 15-5-5L5 20" />
  </Base>
)

export const VideoIcon = (props: IconProps) => (
  <Base {...props}>
    <rect x="3" y="5" width="14" height="14" rx="2" />
    <path d="m17 10 4-2v8l-4-2" />
  </Base>
)

export const CloseIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="m6 6 12 12" />
    <path d="m18 6-12 12" />
  </Base>
)

export const ChevronIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="m9 18 6-6-6-6" />
  </Base>
)

export const ArrowLeftIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="m15 18-6-6 6-6" />
  </Base>
)

export const RefreshIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M20 11a8 8 0 1 0-2.3 5.7" />
    <path d="M20 4v7h-7" />
  </Base>
)

export const ShieldIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" />
    <path d="m9 12 2 2 4-5" />
  </Base>
)

export const EyeIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" />
    <circle cx="12" cy="12" r="2.5" />
  </Base>
)

export const PencilIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M12 20h9" />
    <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" />
  </Base>
)

export const TrashIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M4 7h16" />
    <path d="M10 11v6" />
    <path d="M14 11v6" />
    <path d="m6 7 1 14h10l1-14" />
    <path d="M9 7V4h6v3" />
  </Base>
)
