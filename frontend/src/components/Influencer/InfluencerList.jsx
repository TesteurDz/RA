import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, SlidersHorizontal } from 'lucide-react'
import PlatformBadge from '../common/PlatformBadge'
import LoadingAnimation from '../common/LoadingAnimation'
import { formatNumber, getScoreColor, formatDate } from '../../utils/formatters'
import api from '../../hooks/useApi'

function InfluencerList() {
  const [influencers, setInfluencers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterPlatform, setFilterPlatform] = useState('all')

  useEffect(() => {
    async function fetchData() {
      try {
        const params = filterPlatform !== 'all' ? `?platform=${filterPlatform}` : ''
        const res = await api.get(`/api/influencers/${params}`)
        setInfluencers(res.data.influencers || [])
      } catch (err) {
        console.error('Erreur chargement liste:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [filterPlatform])

  const filtered = searchQuery
    ? influencers.filter(
        (i) =>
          i.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (i.full_name && i.full_name.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : influencers

  if (loading) return <LoadingAnimation text="Chargement..." />

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-[#FAFAFA]">Historique</h2>
        <p className="text-sm text-[#71717A] mt-1">Tous les influenceurs analyses</p>
      </div>

      {/* Search + filters */}
      <div className="space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717A]" />
          <input
            type="text"
            placeholder="Rechercher un influenceur..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-[#18181B] border border-[#27272A] rounded-xl text-sm text-[#FAFAFA] placeholder-[#71717A] focus:outline-none focus:border-[#6366F1] transition-colors duration-200 min-h-[44px]"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-hide">
          <SlidersHorizontal className="w-4 h-4 text-[#71717A] flex-shrink-0" />
          {['all', 'instagram', 'tiktok'].map((p) => (
            <button
              key={p}
              onClick={() => { setFilterPlatform(p); setLoading(true) }}
              className={`text-xs px-3 py-2 rounded-lg whitespace-nowrap transition-all duration-200 flex-shrink-0 min-h-[36px] ${
                filterPlatform === p
                  ? 'bg-[#6366F1] text-white'
                  : 'bg-[#18181B] border border-[#27272A] text-[#A1A1AA] hover:border-[#3F3F46]'
              }`}
            >
              {p === 'all' ? 'Tous' : p === 'instagram' ? 'Instagram' : 'TikTok'}
            </button>
          ))}
        </div>
      </div>

      {/* List */}
      {filtered.length === 0 ? (
        <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-8 text-center">
          <p className="text-sm text-[#71717A]">Aucun influenceur trouve</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((inf) => (
            <Link
              key={inf.id}
              to={`/influencer/${inf.id}`}
              className="block bg-[#18181B] border border-[#27272A] rounded-xl p-4 card-hover transition-all duration-200"
            >
              <div className="flex items-center gap-3">
                {/* Avatar */}
                {inf.profile_pic_url ? (
                  <img
                    src={inf.profile_pic_url}
                    alt={inf.username}
                    className="w-11 h-11 rounded-full object-cover flex-shrink-0 bg-[#27272A]"
                  />
                ) : (
                  <div className="w-11 h-11 rounded-full bg-[#27272A] flex items-center justify-center text-sm font-semibold text-[#71717A] flex-shrink-0">
                    {(inf.username || '?')[0].toUpperCase()}
                  </div>
                )}

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm text-[#FAFAFA] font-medium truncate">
                      {inf.full_name || `@${inf.username}`}
                    </span>
                    {inf.is_verified && (
                      <span className="text-[#6366F1] text-xs">&#10003;</span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <PlatformBadge platform={inf.platform} />
                    <span className="text-xs text-[#71717A]">
                      {formatNumber(inf.followers_count)} abonnes
                    </span>
                    {inf.updated_at && (
                      <span className="text-xs text-[#71717A]">{formatDate(inf.updated_at)}</span>
                    )}
                  </div>
                </div>

                {/* Zone */}
                {inf.zone_operation && (
                  <span className="text-[10px] text-[#A1A1AA] bg-[#27272A] px-2 py-1 rounded-lg hidden md:block flex-shrink-0">
                    {inf.zone_operation}
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default InfluencerList
