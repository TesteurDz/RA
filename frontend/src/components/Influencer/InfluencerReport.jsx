import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { MapPin, CheckCircle, ArrowLeft, Shield } from 'lucide-react'
import ScoreGauge from './ScoreGauge'
import EngagementCard from './EngagementCard'
import FakeFollowersCard from './FakeFollowersCard'
import GrowthChart from './GrowthChart'
import CommentsCard from './CommentsCard'
import DemographicsCard from './DemographicsCard'
import PlatformBadge from '../common/PlatformBadge'
import LoadingAnimation from '../common/LoadingAnimation'
import { formatNumber, getScoreColor, getScoreLabel } from '../../utils/formatters'
import api from '../../hooks/useApi'

function InfluencerReport() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const [infRes, histRes] = await Promise.all([
          api.get(`/api/influencers/${id}`),
          api.get(`/api/influencers/${id}/history`).catch(() => ({ data: { snapshots: [] } })),
        ])
        setData(infRes.data)
        setHistory(histRes.data.snapshots || [])
      } catch (err) {
        setError(err.response?.data?.detail || 'Erreur lors du chargement')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  if (loading) return <LoadingAnimation text="Chargement du rapport..." />

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-[#EF4444] mb-4">{error}</p>
        <button onClick={() => navigate(-1)} className="text-sm text-[#6366F1] hover:text-[#818CF8]">
          Retour
        </button>
      </div>
    )
  }

  if (!data) return null

  const snap = data.latest_snapshot
  const score = snap?.overall_score ?? 0
  const scoreColor = getScoreColor(score)
  const scoreLabel = getScoreLabel(score)

  const stats = [
    { label: 'Followers', value: formatNumber(data.followers_count) },
    { label: 'Following', value: formatNumber(data.following_count) },
    { label: 'Publications', value: formatNumber(data.posts_count) },
    { label: 'Engagement', value: snap ? snap.engagement_rate.toFixed(1) + '%' : 'N/A' },
  ]

  // Verdict
  let verdictType = 'warning'
  let verdictText = ''
  if (score >= 7) {
    verdictType = 'positive'
    verdictText = `Profil authentique avec un score de ${score.toFixed(1)}/10. L'engagement est solide et l'audience semble majoritairement reelle. Recommande pour des collaborations.`
  } else if (score >= 4) {
    verdictType = 'warning'
    verdictText = `Profil moyen avec un score de ${score.toFixed(1)}/10. Quelques indicateurs meritent une attention particuliere. Prudence recommandee avant toute collaboration.`
  } else {
    verdictType = 'danger'
    verdictText = `Profil suspect avec un score de ${score.toFixed(1)}/10. Des indicateurs inquietants ont ete detectes. Deconseille pour des collaborations commerciales.`
  }

  const verdictColors = {
    positive: '#22C55E',
    warning: '#EAB308',
    danger: '#EF4444',
  }
  const vc = verdictColors[verdictType]

  return (
    <div className="space-y-5 max-w-4xl mx-auto">
      {/* Back button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-[#A1A1AA] hover:text-[#FAFAFA] transition-colors min-h-[44px]"
      >
        <ArrowLeft className="w-4 h-4" />
        Retour
      </button>

      {/* Profile header - Fiche technique */}
      <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5 md:p-6">
        <div className="flex flex-col items-center text-center md:flex-row md:items-start md:text-left md:gap-5">
          {/* Avatar */}
          {data.profile_pic_url ? (
            <img
              src={data.profile_pic_url}
              alt={data.username}
              className="w-20 h-20 rounded-full object-cover flex-shrink-0 bg-[#27272A]"
            />
          ) : (
            <div className="w-20 h-20 rounded-full bg-[#27272A] flex items-center justify-center text-2xl font-bold text-[#71717A] flex-shrink-0">
              {(data.username || '?')[0].toUpperCase()}
            </div>
          )}

          {/* Info */}
          <div className="mt-4 md:mt-0 flex-1">
            <div className="flex items-center justify-center md:justify-start gap-2 mb-1">
              <h2 className="text-lg md:text-xl font-bold text-[#FAFAFA]">
                {data.full_name || data.username}
              </h2>
              {data.is_verified && (
                <CheckCircle className="w-4 h-4 text-[#6366F1]" />
              )}
            </div>
            <p className="text-sm text-[#71717A] font-mono mb-2">
              @{data.username}
            </p>
            <div className="flex items-center justify-center md:justify-start gap-3 flex-wrap">
              <PlatformBadge platform={data.platform} />
              {data.zone_operation && (
                <div className="flex items-center gap-1 text-xs text-[#A1A1AA]">
                  <MapPin className="w-3 h-3" />
                  {data.zone_operation}
                </div>
              )}
            </div>
            {data.bio && (
              <p className="text-xs text-[#A1A1AA] mt-2 max-w-md">{data.bio}</p>
            )}
          </div>
        </div>

        {/* Score */}
        <div className="flex justify-center mt-6">
          <ScoreGauge score={score} size={140} />
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6 pt-5 border-t border-[#27272A]">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="bg-[#09090B] border border-[#27272A] rounded-xl p-3 text-center"
            >
              <p className="text-base md:text-lg font-bold font-mono text-[#FAFAFA]">
                {stat.value}
              </p>
              <p className="text-[10px] uppercase tracking-wider text-[#71717A] mt-0.5">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Analysis cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <EngagementCard
          rate={snap?.engagement_rate}
          avgLikes={snap?.avg_likes}
          avgComments={snap?.avg_comments}
          avgShares={snap?.avg_shares}
        />
        <FakeFollowersCard fakePct={snap?.fake_followers_pct} />
        <GrowthChart snapshots={history} />
        <CommentsCard commentAnalysis={snap?.comment_analysis} />
        <DemographicsCard demographic={snap?.audience_demographic} />

        {/* Zone d'operation */}
        {data.zone_operation && (
          <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <MapPin className="w-4 h-4 text-[#EAB308]" />
              <h3 className="text-sm font-semibold text-[#FAFAFA]">Zone d'operation</h3>
            </div>
            <div className="space-y-3">
              <div className="bg-[#09090B] border border-[#27272A] rounded-lg p-3">
                <p className="text-[10px] uppercase tracking-wider text-[#71717A] mb-1">Localisation</p>
                <p className="text-sm font-medium text-[#FAFAFA]">{data.zone_operation}</p>
              </div>
              {data.country && (
                <div className="bg-[#09090B] border border-[#27272A] rounded-lg p-3">
                  <p className="text-[10px] uppercase tracking-wider text-[#71717A] mb-1">Pays</p>
                  <p className="text-sm font-medium text-[#FAFAFA]">{data.country}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Verdict */}
      <div
        className="rounded-xl p-5 md:p-6"
        style={{
          backgroundColor: `${vc}10`,
          border: `1px solid ${vc}30`,
        }}
      >
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-5 h-5" style={{ color: vc }} />
          <h3 className="text-base font-bold uppercase tracking-wider" style={{ color: vc }}>
            Verdict
          </h3>
        </div>
        <p className="text-sm leading-relaxed text-[#FAFAFA]">
          {verdictText}
        </p>
      </div>
    </div>
  )
}

export default InfluencerReport
