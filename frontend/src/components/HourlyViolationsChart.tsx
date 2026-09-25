import type { Analysis } from '../types'

interface HourlyViolation {
  time_slot: string
  count: number
}

interface HourlyViolationsData {
  hourly_violations: HourlyViolation[]
  peak_hour: HourlyViolation | null
}

export function HourlyViolationsChart({ analysis }: { analysis: Analysis }) {
  if (!analysis.hourly_violations) {
    return null
  }

  const data = analysis.hourly_violations as HourlyViolationsData
  const violations = data.hourly_violations || []
  const maxCount = Math.max(...violations.map(v => v.count), 1)

  if (violations.length === 0) {
    return null
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Phân tích theo giờ</p>
          <h2>Vi phạm theo khung giờ</h2>
        </div>
        {data.peak_hour && (
          <div className="peak-hour-badge">
            <span>Cao điểm</span>
            <strong>{data.peak_hour.time_slot}</strong>
          </div>
        )}
      </div>

      <div className="hourly-violations-container">
        {/* Biểu đồ cột */}
        <div className="hourly-chart">
          <div className="chart-bars">
            {violations.map((violation, idx) => (
              <div key={idx} className="bar-wrapper">
                <div className="bar-container">
                  <div
                    className={`bar ${data.peak_hour?.time_slot === violation.time_slot ? 'bar-peak' : ''}`}
                    style={{
                      height: `${(violation.count / maxCount) * 200}px`,
                    }}
                    title={`${violation.time_slot}: ${violation.count} xe vi phạm`}
                  >
                    <span className="bar-value">{violation.count}</span>
                  </div>
                </div>
                <div className="bar-label">{violation.time_slot}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Bảng chi tiết */}
        <div className="hourly-table">
          <table>
            <thead>
              <tr>
                <th>Khung giờ</th>
                <th>Số xe vi phạm</th>
                <th>Tỷ trọng</th>
              </tr>
            </thead>
            <tbody>
              {violations.map((violation, idx) => (
                <tr
                  key={idx}
                  className={data.peak_hour?.time_slot === violation.time_slot ? 'row-peak' : ''}
                >
                  <td className="time-slot">
                    {violation.time_slot}
                    {data.peak_hour?.time_slot === violation.time_slot && (
                      <span className="peak-badge">Cao điểm</span>
                    )}
                  </td>
                  <td className="violation-count">
                    <strong>{violation.count}</strong>
                  </td>
                  <td className="violation-percentage">
                    <div className="percentage-bar">
                      <div
                        className="percentage-fill"
                        style={{
                          width: `${(violation.count / maxCount) * 100}%`,
                        }}
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Thống kê tóm tắt */}
          {data.peak_hour && (
            <div className="hourly-summary">
              <div className="summary-item">
                <span>Khung giờ cao điểm</span>
                <strong>{data.peak_hour.time_slot}</strong>
              </div>
              <div className="summary-item">
                <span>Số xe vi phạm cao nhất</span>
                <strong className="danger-number">{data.peak_hour.count} xe</strong>
              </div>
              <div className="summary-item">
                <span>Tổng khung giờ</span>
                <strong>{violations.length} khung</strong>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
