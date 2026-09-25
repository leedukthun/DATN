import { Navigate, Route, Routes } from 'react-router-dom'
import { RequireAuth } from './auth/RequireAuth'
import { AppShell } from './components/AppShell'
import { AnalysisDetail } from './pages/AnalysisDetail'
import { AuthPage } from './pages/AuthPage'
import { Dashboard } from './pages/Dashboard'
import { LocationDetail } from './pages/LocationDetail'
import { LocationHourlyStats } from './pages/LocationHourlyStats'
import { ProjectDetail } from './pages/ProjectDetail'
import { UploadPage } from './pages/UploadPage'
import { StatisticsPage } from './pages/StatisticsPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage mode="login" />} />
      <Route path="/register" element={<AuthPage mode="register" />} />
      <Route element={<RequireAuth />}>
        <Route element={<AppShell />}>
          <Route index element={<Dashboard />} />
          <Route path="upload" element={<UploadPage />} />
          <Route path="results" element={<StatisticsPage results />} />
          <Route path="statistics" element={<StatisticsPage />} />
          <Route path="projects/:projectId" element={<ProjectDetail />} />
          <Route path="locations/:locationId" element={<LocationDetail />} />
          <Route path="locations/:locationId/hourly-stats" element={<LocationHourlyStats />} />
          <Route path="analyses/:analysisId" element={<AnalysisDetail />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Route>
    </Routes>
  )
}
