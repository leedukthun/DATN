import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeftIcon } from '../components/Icons'
import { ErrorPage, LoadingPage } from '../components/PageState'
import { StatCard } from '../components/StatCard'
import { api } from '../services/api'
import type { Location, LocationHourlyStatistics } from '../types'
import { formatPercent } from '../utils'

export function LocationHourlyStats() {
  const { locationId } = useParams()
  const navigate = useNavigate()
  const id = Number(locationId)
  const [location, setLocation] = useState<Location | null>(null)
  const [stats, setStats] = useState<LocationHourlyStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    if (!id) return
    setError('')
    try {
      const [locationRow, statsRow] = await Promise.all([
        api.location(id),
        api.locationHourlyStatistics(id),
      ])
      setLocation(locationRow)
      setStats(statsRow)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Không thể tải thống kê.')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { void load() }, [load])

  if (loading) return <LoadingPage text="Đang tải thống kê theo giờ..." />
  if (error || !location || !stats) return <ErrorPage message={error || 'Không tìm thấy thống kê.'} onRetry={() => void load()} />

  const maxViolations = Math.max(1, ...(stats.hourly_violations.map((item) => item.count) || [1]))

  return (
    <div className="page">
      <div className="page-header">
        <div className="header-content">
          <button className="icon-btn" onClick={() => navigate(-1)} title="Quay lại">
            <ArrowLeftIcon />
          </button>
          <h1>Thống kê vi phạm theo giờ</h1>
        </div>
      </div>

      <div className="page-body">
        <div className="section">
          <div className="section-header">
            <h2>{location.name}</h2>
          </div>

          <div className="stats-grid">
            <StatCard label="Tổng phiên" value={stats.total_sessions} />
            <StatCard label="Tổng vi phạm" value={stats.total_violations} />
            {stats.peak_hour && (
              <>
                <StatCard label="Khung giờ cao điểm" value={stats.peak_hour.time_slot} />
                <StatCard label="Vi phạm cao điểm" value={stats.peak_hour.count} tone="danger" />
              </>
            )}
          </div>
        </div>

        <div className="section">
          <div className="section-header">
            <h3>Vi phạm theo khung giờ (sắp xếp từ cao tới thấp)</h3>
          </div>

          <div className="hourly-violations-container-full">
            <div className="hourly-chart-full">
              <div className="chart-bars-full">
                {stats.hourly_violations.length === 0 ? (
                  <div className="empty-state">Không có dữ liệu vi phạm</div>
                ) : (
                  stats.hourly_violations.map((slot, idx) => {
                    const height = (slot.count / maxViolations) * 200
                    const isPeak = stats.peak_hour && slot.time_slot === stats.peak_hour.time_slot
                    return (
                      <div key={idx} className="bar-wrapper">
                        <div className="bar-container">
                          <div
                            className={`bar ${isPeak ? 'bar-peak' : ''}`}
                            style={{ height: `${height}px` }}
                          >
                            <div className="bar-value">{slot.count}</div>
                          </div>
                        </div>
                        <div className="bar-label">{slot.time_slot}</div>
                      </div>
                    )
                  })
                )}
              </div>
            </div>

            <div className="hourly-table-full">
              {stats.hourly_violations.length === 0 ? (
                <div className="empty-state">Không có dữ liệu vi phạm</div>
              ) : (
                <>
                  <table>
                    <thead>
                      <tr>
                        <th>Khung giờ</th>
                        <th>Số xe vi phạm</th>
                        <th>Số phiên</th>
                        <th>Tỷ trọng</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stats.hourly_violations.map((slot, idx) => {
                        const percentage = (slot.count / stats.total_violations) * 100
                        const isPeak = stats.peak_hour && slot.time_slot === stats.peak_hour.time_slot
                        return (
                          <tr key={idx} className={isPeak ? 'row-peak' : ''}>
                            <td className="time-slot">
                              {slot.time_slot}
                              {isPeak && <span className="peak-badge">Cao điểm</span>}
                            </td>
                            <td className="violation-count">{slot.count}</td>
                            <td>{slot.sessions}</td>
                            <td className="violation-percentage">
                              <div className="percentage-bar">
                                <div
                                  className="percentage-fill"
                                  style={{ width: `${percentage}%` }}
                                />
                              </div>
                              <span style={{ fontSize: '0.75rem', marginTop: '2px' }}>
                                {percentage.toFixed(1)}%
                              </span>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>

                  <div className="hourly-summary-full">
                    <div className="summary-item">
                      <span>Tổng khung giờ</span>
                      <strong>{stats.hourly_violations.length}</strong>
                    </div>
                    <div className="summary-item">
                      <span>Khung giờ cao điểm</span>
                      <strong>{stats.peak_hour?.time_slot || 'N/A'}</strong>
                    </div>
                    <div className="summary-item">
                      <span>Vi phạm cao nhất</span>
                      <strong>{stats.peak_hour?.count || 0} xe</strong>
                    </div>
                    <div className="summary-item">
                      <span>Trung bình / khung</span>
                      <strong>
                        {stats.hourly_violations.length > 0
                          ? (stats.total_violations / stats.hourly_violations.length).toFixed(1)
                          : '0'}
                      </strong>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
