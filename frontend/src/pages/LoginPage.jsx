import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ScanSearch } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import { Spinner } from '../components/Loaders.jsx'
import AuthShell from '../components/AuthShell.jsx'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('demo@resumeai.com')
  const [password, setPassword] = useState('demopassword123')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password)
      // Route through the welcome transition, preserving any intended destination
      navigate('/welcome', { state: { next: location.state?.next || '/analyze' } })
    } catch (err) {
      const message = !err.response
        ? 'Cannot reach the ResumeAI server. Check that VITE_API_URL points to your deployed backend.'
        : err.response.data?.detail || 'Could not sign in. Check your email and password.'
      toast.error(message, { id: 'auth-error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Sign in to pick up your candidate pipeline where you left off."
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-1 block">Email</label>
          <input className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div>
          <label className="text-sm font-medium mb-1 block">Password</label>
          <input className="input" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button className="btn-primary w-full" type="submit" disabled={loading}>
          {loading && <Spinner className="h-4 w-4" />}
          Sign in
        </button>
      </form>
      <p className="mt-6 text-sm text-ink/60 dark:text-paper/60">
        New to ResumeAI?{' '}
        <Link to="/register" className="text-brand-600 dark:text-brand-300 font-medium hover:underline">
          Create an account
        </Link>
      </p>
      <p className="mt-3 text-xs text-ink/40 dark:text-paper/40">
        Demo login is pre-filled — run <code className="font-mono">seed_demo_data.py</code> on the backend first.
      </p>
    </AuthShell>
  )
}
