import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './context/AuthContext.jsx'
import AppShell from './components/AppShell.jsx'
import CareerShell from './components/CareerShell.jsx'

// Public
import LandingPage from './pages/LandingPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'

// Candidate career flow
import WelcomeTransition from './pages/WelcomeTransition.jsx'
import AnalyzePage from './pages/AnalyzePage.jsx'
import AssessmentPage from './pages/AssessmentPage.jsx'
import ReportPage from './pages/ReportPage.jsx'
import ReportsListPage from './pages/ReportsListPage.jsx'

// Recruiter tools (preserved from the original build)
import DashboardPage from './pages/DashboardPage.jsx'
import JobsPage from './pages/JobsPage.jsx'
import JobDetailPage from './pages/JobDetailPage.jsx'
import ResumeLibraryPage from './pages/ResumeLibraryPage.jsx'
import CandidateDetailPage from './pages/CandidateDetailPage.jsx'

/** Protects a route and wraps it in the candidate-facing shell. */
function CareerRoute({ children, bare = false }) {
  const { isAuthenticated } = useAuth()
  const location = useLocation()
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ next: location.pathname }} replace />
  }
  return bare ? children : <CareerShell>{children}</CareerShell>
}

/** Protects a route and wraps it in the recruiter sidebar shell. */
function RecruiterRoute({ children }) {
  const { isAuthenticated } = useAuth()
  const location = useLocation()
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ next: location.pathname }} replace />
  }
  return <AppShell>{children}</AppShell>
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Candidate career flow */}
      <Route path="/welcome" element={<CareerRoute bare><WelcomeTransition /></CareerRoute>} />
      <Route path="/analyze" element={<CareerRoute><AnalyzePage /></CareerRoute>} />
      <Route path="/assessment/:reportId" element={<CareerRoute><AssessmentPage /></CareerRoute>} />
      <Route path="/report/:reportId" element={<CareerRoute><ReportPage /></CareerRoute>} />
      <Route path="/reports" element={<CareerRoute><ReportsListPage /></CareerRoute>} />

      {/* Recruiter tools — original functionality, preserved */}
      <Route path="/recruiter" element={<RecruiterRoute><DashboardPage /></RecruiterRoute>} />
      <Route path="/recruiter/jobs" element={<RecruiterRoute><JobsPage /></RecruiterRoute>} />
      <Route path="/recruiter/jobs/:jobId" element={<RecruiterRoute><JobDetailPage /></RecruiterRoute>} />
      <Route
        path="/recruiter/jobs/:jobId/candidates/:resumeId"
        element={<RecruiterRoute><CandidateDetailPage /></RecruiterRoute>}
      />
      <Route path="/recruiter/resumes" element={<RecruiterRoute><ResumeLibraryPage /></RecruiterRoute>} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
