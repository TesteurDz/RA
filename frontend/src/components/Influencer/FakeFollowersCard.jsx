import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { ShieldAlert } from 'lucide-react'

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#18181B] border border-[#27272A] rounded-lg px-3 py-2 text-xs">
        <p className="font-mono" style={{ color: payload[0].payload.color }}>
          {payload[0].name}: {payload[0].value}%
        </p>
      </div>
    )
  }
  return null
}

function FakeFollowersCard({ fakePct }) {
  const fake = fakePct != null ? Math.round(fakePct) : 0
  const real = Math.max(0, 100 - fake)

  const chartData = [
    { name: 'Reels', value: real, color: '#22C55E' },
    { name: 'Suspects', value: fake, color: '#EF4444' },
  ]

  return (
    <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <ShieldAlert className="w-4 h-4 text-[#EAB308]" />
        <h3 className="text-sm font-semibold text-[#FAFAFA]">Faux followers</h3>
      </div>

      <ResponsiveContainer width="100%" height={180}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={72}
            paddingAngle={3}
            dataKey="value"
            strokeWidth={0}
          >
            {chartData.map((entry, index) => (
              <Cell key={index} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      <div className="flex justify-center gap-6 mt-3">
        {chartData.map((item) => (
          <div key={item.name} className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="text-xs text-[#A1A1AA]">{item.name}</span>
            <span className="text-xs font-bold font-mono" style={{ color: item.color }}>
              {item.value}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default FakeFollowersCard
