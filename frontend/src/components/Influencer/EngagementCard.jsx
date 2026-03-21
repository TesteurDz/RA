import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { Heart } from 'lucide-react'

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#18181B] border border-[#27272A] rounded-lg px-3 py-2 text-xs">
        <p className="text-[#71717A]">{label}</p>
        <p className="text-[#6366F1] font-mono font-bold">{payload[0].value}%</p>
      </div>
    )
  }
  return null
}

function EngagementCard({ rate, avgLikes, avgComments, avgShares }) {
  const breakdown = [
    { label: 'Likes', value: avgLikes || 0 },
    { label: 'Comm.', value: avgComments || 0 },
    { label: 'Partages', value: avgShares || 0 },
  ].filter(item => item.value > 0)

  return (
    <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Heart className="w-4 h-4 text-[#6366F1]" />
        <h3 className="text-sm font-semibold text-[#FAFAFA]">Taux d'engagement</h3>
      </div>

      <div className="text-center mb-5">
        <span className="text-4xl font-bold font-mono text-[#6366F1]">
          {rate != null ? rate.toFixed(1) : '0'}%
        </span>
        <p className="text-xs text-[#71717A] mt-1">Engagement global</p>
      </div>

      {breakdown.length > 0 && (
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={breakdown} barSize={32}>
            <XAxis dataKey="label" stroke="#71717A" tick={{ fontSize: 11, fill: '#71717A' }} axisLine={false} tickLine={false} />
            <YAxis stroke="#71717A" tick={{ fontSize: 10, fill: '#71717A' }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} cursor={false} />
            <Bar dataKey="value" fill="#6366F1" radius={[6, 6, 0, 0]} opacity={0.8} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

export default EngagementCard
