import { Search, MapPin } from 'lucide-react'

function Header() {
  return (
    <header
      className="fixed top-0 left-0 right-0 z-40 lg:ml-60"
      style={{ paddingTop: 'env(safe-area-inset-top, 0px)' }}
    >
      <div className="h-14 lg:h-16 border-b border-[#27272A] bg-[#09090B]/80 backdrop-blur-xl flex items-center justify-between px-5 lg:px-8">
        {/* Mobile: RA text */}
        <div className="lg:hidden">
          <h1 className="text-lg font-bold text-[#FAFAFA] tracking-tight">RA</h1>
        </div>

        {/* Desktop: Search bar */}
        <div className="hidden lg:block relative w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717A]" />
          <input
            type="text"
            placeholder="Rechercher un influenceur..."
            className="w-full pl-10 pr-4 py-2 bg-[#18181B] border border-[#27272A] rounded-xl text-sm text-[#FAFAFA] placeholder-[#71717A] focus:outline-none focus:border-[#6366F1] transition-colors duration-200"
          />
        </div>

        {/* Right: Zone badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-[#18181B] border border-[#27272A] rounded-xl">
          <MapPin className="w-3.5 h-3.5 text-[#6366F1]" />
          <span className="text-xs text-[#A1A1AA] font-medium">Algerie</span>
        </div>
      </div>
    </header>
  )
}

export default Header
