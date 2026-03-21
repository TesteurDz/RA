function LoadingAnimation({ text = 'Chargement...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4">
      <svg className="w-10 h-10 mb-4 animate-spin" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="#27272A" strokeWidth="3" />
        <path
          d="M12 2a10 10 0 0 1 10 10"
          stroke="#6366F1"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
      <p className="text-sm text-[#A1A1AA]">{text}</p>
    </div>
  )
}

export default LoadingAnimation
