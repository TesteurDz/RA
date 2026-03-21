import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Search, Users, GitCompareArrows } from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Accueil' },
  { to: '/analyze', icon: Search, label: 'Analyser' },
  { to: '/influencers', icon: Users, label: 'Historique' },
  { to: '/compare', icon: GitCompareArrows, label: 'Comparer' },
]

function Sidebar() {
  return (
    <>
      <MobileBottomNav />
      <DesktopSidebar />
    </>
  )
}

function MobileBottomNav() {
  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 lg:hidden"
      style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
    >
      <div className="absolute inset-0 bg-[#09090B]/80 backdrop-blur-xl border-t border-[#27272A]" />
      <div className="relative flex items-center justify-around h-14 px-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center gap-1 min-w-[56px] min-h-[48px] px-3 py-1.5 rounded-xl transition-all duration-200 ${
                isActive ? 'text-white' : 'text-[#71717A]'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div className={`p-1.5 rounded-lg transition-colors duration-200 ${isActive ? 'bg-[#6366F1]' : ''}`}>
                  <item.icon className="w-5 h-5" strokeWidth={isActive ? 2 : 1.5} />
                </div>
                <span className={`text-[10px] font-medium leading-none ${isActive ? 'text-[#FAFAFA]' : 'text-[#71717A]'}`}>
                  {item.label}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}

function DesktopSidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-[#09090B] border-r border-[#27272A] flex-col z-50 hidden lg:flex">
      <div className="p-6 border-b border-[#27272A]">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold tracking-tight text-[#FAFAFA]">
            RA
          </h1>
          <span className="text-xs text-[#71717A] font-medium">
            Reputation Analyzer
          </span>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 ${
                isActive
                  ? 'bg-[#6366F1] text-white'
                  : 'text-[#A1A1AA] hover:bg-[#27272A] hover:text-[#FAFAFA]'
              }`
            }
          >
            <item.icon className="w-[18px] h-[18px]" />
            <span className="text-sm font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-[#27272A]">
        <div className="flex items-center gap-2 px-3 py-2">
          <div className="w-2 h-2 rounded-full bg-[#22C55E]" />
          <span className="text-xs text-[#71717A]">
            RA v1.0
          </span>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
