import { useState, useEffect } from 'react'
import { Users, TrendingUp, Eye, AlertTriangle, ChevronRight } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import StatCard from './StatCard'
import { formatNumber, getScoreColor, getScoreLabel, formatDate } from '../../utils/formatters'
import PlatformBadge from '../common/PlatformBadge'
import LoadingAnimation from '../common/LoadingAnimation'
import api from '../../hooks/useApi'

function DashboardPage() {
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [recent, setRecent] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, recentRes] = await Promise.all([
          api.get('/api/dashboard/stats'),
          api.get('/api/dashboard/recent'),
        ])
        setStats(statsRes.data)
        setRecent(recentRes.data.recent || [])
      } catch (err) {
        console.error('Erreur chargement dashboard:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return <LoadingAnimation text="Chargement du tableau de bord..." />
  }

  return (
    <div className="space-y-6">
      {/* Titre */}
      <div>
        <h2 className="text-xl font-bold text-[#FAFAFA]">Tableau de bord</h2>
        <p className="text-sm text-[#71717A] mt-1">Vue d'ensemble de vos analyses</p>
      </div>

      {/* Stats 2x2 */}
      <div className="grid grid-cols-2 gap-3 lg:gap-4">
        <StatCard
          icon={Users}
          value={stats?.total_analyzed ?? 0}
          label="Total analyses"
          color="#6366F1"
        />
        <StatCard
          icon={TrendingUp}
          value={stats?.avg_overall_score?.toFixed(1) ?? '0'}
          label="Score moyen"
          color="#22C55E"
        />
        <StatCard
          icon={Eye}
          value={stats?.avg_engagement_rate ? stats.avg_engagement_rate.toFixed(1) + '%' : '0%'}
          label="Engagement moyen"
          color="#EAB308"
        />
        <StatCard
          icon={AlertTriangle}
          value={stats?.avg_fake_followers_pct ? stats.avg_fake_followers_pct.toFixed(0) + '%' : '0%'}
          label="Faux followers moy."
          color="#EF4444"
        />
      </div>

      {/* Analyses recentes */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-[#FAFAFA]">Analyses recentes</h3>
          <Link
            to="/influencers"
            className="text-xs text-[#6366F1] flex items-center gap-1 min-h-[44px] hover:text-[#818CF8] transition-colors"
          >
            Tout voir <ChevronRight className="w-3 h-3" />
          </Link>
        </div>

        {recent.length === 0 ? (
          <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-8 text-center">
            <p className="text-sm text-[#71717A]">Aucune analyse pour le moment</p>
            <Link to="/analyze" className="text-sm text-[#6366F1] mt-2 inline-block hover:text-[#818CF8]">
              Lancer votre premiere analyse
            </Link>
          </div>
        ) : (
          <div className="space-y-2">
            {recent.map((a) => (
              <button
                key={a.id}
                onClick={() => navigate(`/influencer/${a.id}`)}
                className="w-full bg-[#18181B] border border-[#27272A] rounded-xl p-4 card-hover text-left transition-all duration-200"
              >
                <div className="flex items-center gap-3">
                  {/* Avatar */}
                  {a.profile_pic_url ? (
                    <img
                      src={a.profile_pic_url}
                      alt={a.username}
                      className="w-10 h-10 rounded-full object-cover flex-shrink-0 bg-[#27272A]"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-[#27272A] flex items-center justify-center text-sm font-semibold text-[#71717A] flex-shrink-0">
                      {(a.username || '?')[0].toUpperCase()}
                    </div>
                  )}

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-sm text-[#FAFAFA] font-medium truncate">
                        {a.full_name || `@${a.username}`}
                      </span>
                      <PlatformBadge platform={a.platform} />
                    </div>
                    <div className="flex items-center gap-3 text-xs text-[#71717A]">
                      <span>{formatNumber(a.followers_count)} abonnes</span>
                      {a.engagement_rate != null && <span>Eng. {a.engagement_rate.toFixed(1)}%</span>}
                      {a.analyzed_at && <span>{formatDate(a.analyzed_at)}</span>}
                    </div>
                  </div>

                  {/* Score */}
                  {a.overall_score != null && (
                    <div className="flex flex-col items-center flex-shrink-0">
                      <span
                        className="text-lg font-mono font-bold leading-none"
                        style={{ color: getScoreColor(a.overall_score) }}
                      >
                        {a.overall_score.toFixed(1)}
                      </span>
                      <span
                        className="text-[8px] font-mono uppercase tracking-wider mt-0.5"
                        style={{ color: getScoreColor(a.overall_score) }}
                      >
                        {getScoreLabel(a.overall_score)}
                      </span>
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
