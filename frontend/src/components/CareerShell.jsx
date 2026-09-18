import { Link, NavLink, useNavigate } from 'react-router-dom'
import { ScanSearch, Sun, Moon, LogOut, LayoutGrid, FilePlus2, History } from 'lucide-react'
import clsx from 'clsx'
import { useAuth } from '../context/AuthContext.jsx'
import { useTheme } from '../context/ThemeContext.jsx'

const NAV = [
  { to: '/analyze', label: 'New analysis', icon: FilePlus2 },
  { to: '/reports', label: 'My reports', icon: History },
  { to: '/recruiter', label: 'Recruiter tools', icon: LayoutGrid },
]

export default function CareerShell({ children }) {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-paper dark:bg-ink text-ink dark:text-paper flex flex-col">
      <header className="sticky top-0 z-40 border-b border-line dark:border-lineDark bg-paper/85 dark:bg-ink/85 backdrop-blur">
        <div className="container-page flex h-16 items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <ScanSearch className="h-5 w-5 text-brand-600 dark:text-brand-300" strokeWidth={2} />
            <span className="font-display text-lg tracking-tight hidden sm:inline">ResumeAI</span>
          </Link>

          <nav className="flex items-center gap-1 overflow-x-auto">
            {NAV.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium whitespace-nowrap transition-colors',
                    isActive
                      ? 'bg-brand-600 text-white'
                      : 'text-ink/70 hover:bg-black/5 dark:text-paper/70 dark:hover:bg-white/5'
                  )
                }
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-1 shrink-0">
            <button onClick={toggleTheme} className="btn-ghost !px-2" aria-label="Toggle theme">
              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <div className="hidden md:flex items-center gap-2 pl-2">
              <div className="h-8 w-8 rounded-full bg-brand-100 dark:bg-brand-500/30 flex items-center justify-center text-sm font-medium text-brand-700 dark:text-brand-100">
                {(user?.full_name || user?.email || '?')[0].toUpperCase()}
              </div>
              <button onClick={handleLogout} className="btn-ghost !px-2" title="Log out">
                <LogOut className="h-4 w-4" />
              </button>
            </div>
            <button onClick={handleLogout} className="md:hidden btn-ghost !px-2" title="Log out">
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1">{children}</main>
    </div>
  )
}
