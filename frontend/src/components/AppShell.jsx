import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Briefcase, FileText, Sun, Moon, LogOut, ScanSearch, Menu, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import { useTheme } from '../context/ThemeContext.jsx'
import clsx from 'clsx'

const NAV_ITEMS = [
  { to: '/recruiter', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/recruiter/jobs', label: 'Jobs', icon: Briefcase },
  { to: '/recruiter/resumes', label: 'Resume library', icon: FileText },
]

export default function AppShell({ children }) {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navigation = (
    <nav className="flex-1 px-3 py-4 space-y-1">
      {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={() => setMenuOpen(false)}
          className={({ isActive }) =>
            clsx(
              'flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors',
              isActive
                ? 'bg-brand-600 text-white'
                : 'text-ink/70 hover:bg-black/5 dark:text-paper/70 dark:hover:bg-white/5'
            )
          }
        >
          <Icon className="h-4 w-4" strokeWidth={2} />
          {label}
        </NavLink>
      ))}
    </nav>
  )

  const account = (
    <div className="px-3 py-4 border-t border-line dark:border-lineDark space-y-1">
      <button onClick={toggleTheme} className="btn-ghost w-full justify-start">
        {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        {theme === 'dark' ? 'Light mode' : 'Dark mode'}
      </button>
      <div className="flex items-center gap-3 px-3 py-2">
        <div className="h-8 w-8 rounded-full bg-brand-100 dark:bg-brand-500/30 flex items-center justify-center text-sm font-medium text-brand-700 dark:text-brand-100">
          {(user?.full_name || user?.email || '?')[0].toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{user?.full_name || 'Recruiter'}</p>
          <p className="text-xs text-ink/50 dark:text-paper/50 truncate">{user?.email}</p>
        </div>
        <button onClick={handleLogout} title="Log out" className="text-ink/40 hover:text-ink dark:text-paper/40 dark:hover:text-paper">
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen flex bg-paper dark:bg-ink text-ink dark:text-paper">
      <aside className="hidden md:flex w-60 shrink-0 border-r border-line dark:border-lineDark flex-col">
        <div className="h-16 flex items-center gap-2 px-5 border-b border-line dark:border-lineDark">
          <ScanSearch className="h-5 w-5 text-brand-600 dark:text-brand-300" strokeWidth={2} />
          <span className="font-display text-lg tracking-tight">ResumeAI</span>
        </div>
        {navigation}
        {account}
      </aside>

      <div className="flex-1 min-w-0">
        <header className="md:hidden sticky top-0 z-30 h-16 flex items-center justify-between px-5 border-b border-line dark:border-lineDark bg-paper/90 dark:bg-ink/90 backdrop-blur">
          <div className="flex items-center gap-2">
            <ScanSearch className="h-5 w-5 text-brand-600 dark:text-brand-300" strokeWidth={2} />
            <span className="font-display text-lg tracking-tight">ResumeAI</span>
          </div>
          <button onClick={() => setMenuOpen((open) => !open)} className="btn-ghost !px-2" aria-label={menuOpen ? 'Close navigation' : 'Open navigation'}>
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </header>
        {menuOpen && (
          <div className="md:hidden fixed inset-0 top-16 z-20 bg-black/20" onClick={() => setMenuOpen(false)}>
            <aside className="w-[min(18rem,88vw)] min-h-full bg-paper dark:bg-ink border-r border-line dark:border-lineDark flex flex-col" onClick={(event) => event.stopPropagation()}>
              {navigation}
              {account}
            </aside>
          </div>
        )}
        <main>{children}</main>
      </div>
    </div>
  )
}
