import { Instagram } from 'lucide-react'

function PlatformBadge({ platform, size = 'sm' }) {
  const isInstagram = platform === 'instagram'
  const sizeClasses = size === 'sm'
    ? 'text-[10px] px-2 py-0.5'
    : 'text-xs px-2.5 py-1'

  return (
    <span
      className={`${sizeClasses} rounded-lg font-medium inline-flex items-center gap-1 ${
        isInstagram
          ? 'bg-[#E1306C]/10 text-[#E1306C] border border-[#E1306C]/20'
          : 'bg-[#FAFAFA]/5 text-[#A1A1AA] border border-[#FAFAFA]/10'
      }`}
    >
      {isInstagram ? (
        <Instagram className="w-3 h-3" />
      ) : (
        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9a6.33 6.33 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.34-6.34V8.75a8.18 8.18 0 004.76 1.52V6.84a4.84 4.84 0 01-1-.15z" />
        </svg>
      )}
      {isInstagram ? 'Instagram' : 'TikTok'}
    </span>
  )
}

export default PlatformBadge
