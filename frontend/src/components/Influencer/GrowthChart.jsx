import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp } from 'lucide-react'
import { formatNumber } from '../../utils/formatters'

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#18181B] border border-[#27272A] rounded-lg px-3 py-2 text-xs">
        <p className="text-[#71717A]">{label}</p>
        <p className="text-[#6366F1] font-mono font-bold">
          {formatNumber(payload[0].value)} followers
        </p>
      </div>
    )
  }
  return null
}

function GrowthChart({ snapshots }) {
  const chartData = (snapshots || []).map((s) => ({
    date: s.captured_at ? new Date(s.captured_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }) : '',
    followers: s.followers_count || 0,
  })).reverse()

  if (chartData.length === 0) {
    return (
      <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-[#6366F1]" />
          <h3 className="text-sm font-semibold text-[#FAFAFA]">Evolution de croissance</h3>
        </div>
        <p className="text-sm text-[#71717A] text-center py-8">
          Pas assez de donnees pour afficher l'evolution
        </p>
      </div>
    )
  }

  return (
    <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-4 h-4 text-[#6366F1]" />
        <h3 className="text-sm font-semibold text-[#FAFAFA]">Evolution de croissance</h3>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <XAxis
            dataKey="date"
            stroke="#71717A"
            tick={{ fontSize: 10, fill: '#71717A' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            stroke="#71717A"
            tick={{ fontSize: 9, fill: '#71717A' }}
            tickFormatter={(v) => formatNumber(v)}
            width={45}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="followers"
            stroke="#6366F1"
            strokeWidth={2}
            dot={{ fill: '#6366F1', strokeWidth: 0, r: 3 }}
            activeDot={{ r: 5, fill: '#6366F1', stroke: '#09090B', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default GrowthChart
