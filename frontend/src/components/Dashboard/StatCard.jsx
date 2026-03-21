function StatCard({ icon: Icon, value, label, color = '#6366F1', onClick }) {
  return (
    <button
      onClick={onClick}
      className="bg-[#18181B] border border-[#27272A] rounded-xl p-4 w-full text-left card-hover transition-all duration-200"
    >
      <div className="flex items-start justify-between mb-3">
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${color}15` }}
        >
          <Icon className="w-4 h-4" style={{ color }} />
        </div>
        <div className="w-2 h-2 rounded-full mt-1" style={{ backgroundColor: color, opacity: 0.6 }} />
      </div>
      <p className="text-2xl font-bold font-mono text-[#FAFAFA] leading-none mb-1">
        {value}
      </p>
      <p className="text-xs text-[#A1A1AA]">{label}</p>
    </button>
  )
}

export default StatCard
