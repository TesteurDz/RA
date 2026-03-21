import { useState, useEffect, useMemo } from 'react'
import { Plus, X, Trophy, ChevronDown } from 'lucide-react'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend } from 'recharts'
import PlatformBadge from '../common/PlatformBadge'
import LoadingAnimation from '../common/LoadingAnimation'
import { formatNumber, getScoreColor } from '../../utils/formatters'
import api from '../../hooks/useApi'

const radarColors = ['#6366F1', '#22C55E', '#EAB308', '#EF4444']

function ComparePage() {
  const [allInfluencers, setAllInfluencers] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedIds, setSelectedIds] = useState([])
  const [selectedData, setSelectedData] = useState([])
  const [dropdownOpen, setDropdownOpen] = useState(false)

  // Load all influencers for selection
  useEffect(() => {
    async function fetchList() {
      try {
        const res = await api.get('/api/influencers/')
        setAllInfluencers(res.data.influencers || [])
      } catch (err) {
        console.error('Erreur:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchList()
  }, [])

  // Load detailed data when selection changes
  useEffect(() => {
    if (selectedIds.length < 2) {
      setSelectedData([])
      return
    }
    async function fetchComparison() {
      try {
        const res = await api.post('/api/influencers/compare', selectedIds)
        setSelectedData(res.data.comparisons || [])
      } catch (err) {
        console.error('Erreur comparaison:', err)
      }
    }
    fetchComparison()
  }, [selectedIds])

  const radarData = useMemo(() => {
    if (selectedData.length < 2) return []
    return [
      { metric: 'Score', ...Object.fromEntries(selectedData.map((s) => [s.username, (s.overall_score || 0) * 10])) },
      { metric: 'Engagement', ...Object.fromEntries(selectedData.map((s) => [s.username, (s.engagement_rate || 0) * 10])) },
      { metric: 'Authenticite', ...Object.fromEntries(selectedData.map((s) => [s.username, 100 - (s.fake_followers_pct || 0)])) },
    ]
  }, [selectedData])

  const bestChoice = useMemo(() => {
    if (selectedData.length < 2) return null
    return selectedData.reduce((best, curr) => ((curr.overall_score || 0) > (best.overall_score || 0) ? curr : best))
  }, [selectedData])

  const addInfluencer = (id) => {
    if (selectedIds.length < 4 && !selectedIds.includes(id)) {
      setSelectedIds([...selectedIds, id])
    }
    setDropdownOpen(false)
  }

  const removeInfluencer = (id) => {
    setSelectedIds(selectedIds.filter((sid) => sid !== id))
  }

  const available = allInfluencers.filter((i) => !selectedIds.includes(i.id))

  if (loading) return <LoadingAnimation text="Chargement..." />

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-[#FAFAFA]">Comparaison</h2>
        <p className="text-sm text-[#71717A] mt-1">Comparez jusqu'a 4 influenceurs</p>
      </div>

      {/* Selected chips */}
      <div className="flex items-center gap-2 flex-wrap">
        {selectedIds.map((id, idx) => {
          const inf = allInfluencers.find((i) => i.id === id)
          if (!inf) return null
          return (
            <div
              key={id}
              className="flex items-center gap-2 px-3 py-2 bg-[#18181B] border rounded-xl min-h-[44px]"
              style={{ borderColor: `${radarColors[idx]}40` }}
            >
              <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: radarColors[idx] }} />
              <span className="text-sm text-[#FAFAFA]">@{inf.username}</span>
              <PlatformBadge platform={inf.platform} />
              <button onClick={() => removeInfluencer(id)} className="ml-1 text-[#71717A] hover:text-[#FAFAFA] p-1 min-w-[28px] min-h-[28px]">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )
        })}

        {selectedIds.length < 4 && (
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 px-3 py-2 bg-[#18181B] border border-dashed border-[#27272A] rounded-xl text-sm text-[#71717A] hover:border-[#3F3F46] transition-colors min-h-[44px]"
            >
              <Plus className="w-4 h-4" />
              Ajouter
              <ChevronDown className="w-3 h-3" />
            </button>
            {dropdownOpen && (
              <div className="absolute top-full mt-2 left-0 w-64 bg-[#18181B] border border-[#27272A] rounded-xl shadow-2xl z-20 overflow-hidden max-h-64 overflow-y-auto">
                {available.map((inf) => (
                  <button
                    key={inf.id}
                    onClick={() => addInfluencer(inf.id)}
                    className="w-full flex items-center gap-2 px-4 py-3 text-sm text-left text-[#FAFAFA] hover:bg-[#27272A] transition-colors min-h-[44px]"
                  >
                    <span>@{inf.username}</span>
                    <PlatformBadge platform={inf.platform} />
                  </button>
                ))}
                {available.length === 0 && (
                  <p className="px-4 py-3 text-xs text-[#71717A]">Aucun influenceur disponible</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {selectedData.length >= 2 && (
        <>
          {/* Radar chart */}
          <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5">
            <h3 className="text-sm font-semibold text-[#FAFAFA] mb-4">Comparaison radar</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#27272A" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: '#A1A1AA', fontSize: 11 }} />
                <PolarRadiusAxis tick={{ fill: '#71717A', fontSize: 8 }} domain={[0, 100]} />
                {selectedData.map((inf, idx) => (
                  <Radar
                    key={inf.id}
                    name={`@${inf.username}`}
                    dataKey={inf.username}
                    stroke={radarColors[idx]}
                    fill={radarColors[idx]}
                    fillOpacity={0.1}
                    strokeWidth={2}
                  />
                ))}
                <Legend wrapperStyle={{ fontSize: '11px' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Comparison table */}
          <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5 overflow-x-auto">
            <h3 className="text-sm font-semibold text-[#FAFAFA] mb-4">Tableau comparatif</h3>
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#27272A]">
                  <th className="text-left text-xs font-medium text-[#71717A] pb-3 pr-4">Metrique</th>
                  {selectedData.map((inf, idx) => (
                    <th key={inf.id} className="text-left text-xs font-medium pb-3 pr-4" style={{ color: radarColors[idx] }}>
                      @{inf.username}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  { label: 'Score', key: 'overall_score', format: (v) => (v || 0).toFixed(1), colorFn: getScoreColor },
                  { label: 'Followers', key: 'followers_count', format: formatNumber },
                  { label: 'Engagement', key: 'engagement_rate', format: (v) => (v || 0).toFixed(1) + '%' },
                  { label: 'Faux followers', key: 'fake_followers_pct', format: (v) => (v || 0).toFixed(0) + '%' },
                ].map((metric) => (
                  <tr key={metric.key} className="border-b border-[#27272A]/50">
                    <td className="py-3 pr-4 text-sm text-[#A1A1AA]">{metric.label}</td>
                    {selectedData.map((inf) => (
                      <td key={inf.id} className="py-3 pr-4">
                        <span
                          className="text-sm font-bold font-mono"
                          style={{ color: metric.colorFn ? metric.colorFn(inf[metric.key]) : '#FAFAFA' }}
                        >
                          {metric.format(inf[metric.key])}
                        </span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Best choice */}
          {bestChoice && (
            <div className="bg-[#22C55E]/5 border border-[#22C55E]/20 rounded-xl p-5">
              <div className="flex items-center gap-3 mb-3">
                <Trophy className="w-5 h-5 text-[#22C55E]" />
                <h3 className="text-base font-bold uppercase tracking-wider text-[#22C55E]">
                  Meilleur choix
                </h3>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-11 h-11 rounded-full bg-[#27272A] flex items-center justify-center text-lg font-bold text-[#22C55E] flex-shrink-0">
                  {(bestChoice.username || '?')[0].toUpperCase()}
                </div>
                <div>
                  <p className="text-base font-bold text-[#FAFAFA]">@{bestChoice.username}</p>
                  <p className="text-sm text-[#A1A1AA] mt-0.5">
                    Score: <span className="font-mono font-bold text-[#22C55E]">{(bestChoice.overall_score || 0).toFixed(1)}</span>
                    {' | '}
                    Engagement: <span className="font-mono font-bold text-[#22C55E]">{(bestChoice.engagement_rate || 0).toFixed(1)}%</span>
                  </p>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {selectedIds.length < 2 && (
        <div className="text-center py-16">
          <p className="text-sm text-[#71717A]">Selectionnez au moins 2 influenceurs pour comparer</p>
        </div>
      )}
    </div>
  )
}

export default ComparePage
