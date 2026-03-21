import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { MessageCircle } from 'lucide-react'

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

function CommentsCard({ commentAnalysis }) {
  const ca = commentAnalysis || {}

  const sentimentData = [
    { name: 'Positif', value: ca.positive_pct || 0, color: '#22C55E' },
    { name: 'Neutre', value: ca.neutral_pct || 0, color: '#71717A' },
    { name: 'Negatif', value: ca.negative_pct || 0, color: '#EF4444' },
  ].filter(d => d.value > 0)

  const hasSentiment = sentimentData.length > 0

  return (
    <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <MessageCircle className="w-4 h-4 text-[#22C55E]" />
        <h3 className="text-sm font-semibold text-[#FAFAFA]">Analyse des commentaires</h3>
      </div>

      {hasSentiment ? (
        <>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={65}
                paddingAngle={3}
                dataKey="value"
                strokeWidth={0}
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>

          <div className="flex flex-wrap gap-3 justify-center mt-2">
            {sentimentData.map((item) => (
              <div key={item.name} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-xs text-[#A1A1AA]">{item.name}</span>
                <span className="text-xs font-bold font-mono" style={{ color: item.color }}>
                  {item.value.toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="text-sm text-[#71717A] text-center py-8">
          Pas de donnees de commentaires disponibles
        </p>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 mt-4">
        <div className="bg-[#09090B] border border-[#27272A] rounded-lg p-3">
          <p className="text-[10px] uppercase tracking-wider text-[#71717A]">Bots detectes</p>
          <p className="text-lg font-bold font-mono mt-1 text-[#EAB308]">
            {(ca.bot_comments_pct || 0).toFixed(0)}%
          </p>
        </div>
        <div className="bg-[#09090B] border border-[#27272A] rounded-lg p-3">
          <p className="text-[10px] uppercase tracking-wider text-[#71717A]">Total analyses</p>
          <p className="text-lg font-bold font-mono mt-1 text-[#FAFAFA]">
            {ca.total_comments_analyzed || 0}
          </p>
        </div>
      </div>
    </div>
  )
}

export default CommentsCard
