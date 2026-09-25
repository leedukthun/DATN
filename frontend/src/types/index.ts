export interface AuthUser {
  id: number
  username: string
  created_at: string
}

export interface Location {
  id: number
  project_id: number
  project_name?: string
  name: string
  description: string | null
  latitude: number | null
  longitude: number | null
  created_at: string
  updated_at: string
}

export interface Project {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
  locations: Location[]
}

export interface MediaFile {
  id: number
  session_id: number
  original_filename: string
  file_type: 'image' | 'video'
  original_url: string
  result_url: string | null
  status: string
  progress: number
  total_vehicles: number
  helmet_count: number
  no_helmet_count: number
  violation_count: number
  error_message: string | null
}

export interface Violation {
  id: number
  session_id: number
  media_id: number
  media_filename?: string | null
  vehicle_id: string | null
  frame_number: number | null
  timestamp_seconds: number | null
  confidence: number
  status: string
  evidence_url: string
  bbox: number[] | null
  created_at: string
}

export interface Analysis {
  id: number
  project_id: number
  project_name: string
  location_id: number
  location_name: string
  analysis_date: string
  start_time: string
  end_time: string
  total_files: number
  processed_files: number
  total_vehicles: number
  helmet_count: number
  no_helmet_count: number
  violation_count: number
  violation_rate: number
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  progress: number
  error_message: string | null
  created_at: string
  completed_at: string | null
  media_files?: MediaFile[]
  violations?: Violation[]
  hourly_violations?: {
    hourly_violations: { time_slot: string; count: number }[]
    peak_hour: { time_slot: string; count: number } | null
  } | null
}

export interface TimeSlotStatistic {
  time_slot: string
  violations: number
}

export interface LocationStatistic {
  location: string
  violations: number
}

export interface Statistics {
  total_sessions: number
  total_vehicles: number
  total_violations: number
  violation_rate: number
  by_time_slot: TimeSlotStatistic[]
  peak_time_slot: TimeSlotStatistic | null
  by_location: LocationStatistic[]
}

export interface HourlyViolationSlot {
  time_slot: string
  count: number
  sessions: number
}

export interface LocationHourlyStatistics {
  total_sessions: number
  total_violations: number
  hourly_violations: HourlyViolationSlot[]
  peak_hour: HourlyViolationSlot | null
}

export interface ProjectPayload {
  name: string
  description?: string
}

export interface LocationPayload {
  name: string
  description?: string
  latitude?: number | null
  longitude?: number | null
}
