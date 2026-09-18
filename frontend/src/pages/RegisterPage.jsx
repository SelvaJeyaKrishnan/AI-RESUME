import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext.jsx'
import { Spinner } from '../components/Loaders.jsx'
import AuthShell from '../components/AuthShell.jsx'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ full_name: '', company_name: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await register(form)
      navigate('/welcome', { state: { next: '/analyze' } })
    } catch (err) {
      const message = !err.response || err.response.status === 404
        ? 'Cannot reach the ResumeAI server. Set VITE_API_URL to your deployed backend URL in Vercel.'
        : err.response.data?.detail || 'Could not create your account.'
      toast.error(message, { id: 'auth-error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="Set up ResumeAI for your hiring team in under a minute."
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-1 block">Full name</label>
          <input className="input" required value={form.full_name} onChange={update('full_name')} />
        </div>
        <div>
          <label className="text-sm font-medium mb-1 block">Company</label>
          <input className="input" value={form.company_name} onChange={update('company_name')} />
        </div>
        <div>
          <label className="text-sm font-medium mb-1 block">Email</label>
          <input className="input" type="email" required value={form.email} onChange={update('email')} />
        </div>
        <div>
          <label className="text-sm font-medium mb-1 block">Password</label>
          <input className="input" type="password" required minLength={8} value={form.password} onChange={update('password')} />
          <p className="text-xs text-ink/40 dark:text-paper/40 mt-1">At least 8 characters.</p>
        </div>
        <button className="btn-primary w-full" type="submit" disabled={loading}>
          {loading && <Spinner className="h-4 w-4" />}
          Create account
        </button>
      </form>
      <p className="mt-6 text-sm text-ink/60 dark:text-paper/60">
        Already have an account?{' '}
        <Link to="/login" className="text-brand-600 dark:text-brand-300 font-medium hover:underline">
          Sign in
        </Link>
      </p>
    </AuthShell>
  )
}
