import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Camera, AlertCircle } from 'lucide-react'
import ScreenshotUpload from './ScreenshotUpload'
import api from '../../hooks/useApi'

function AnalyzePage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [platform, setPlatform] = useState('instagram')
  const [mode, setMode] = useState('username')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (!username.trim()) return
    setIsAnalyzing(true)
    setError(null)
    try {
      const res = await api.post(`/api/influencers/analyze?username=${encodeURIComponent(username.trim())}&platform=${platform}`)
      navigate(`/influencer/${res.data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'analyse')
      setIsAnalyzing(false)
    }
  }

  const handleScreenshotResult = (data) => {
    if (data.influencer_id) {
      navigate(`/influencer/${data.influencer_id}`)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleAnalyze()
  }

  return (
    <div className="space-y-6">
      {/* Titre */}
      <div>
        <h2 className="text-xl font-bold text-[#FAFAFA]">Nouvelle analyse</h2>
        <p className="text-sm text-[#71717A] mt-1">Analysez la reputation d'un influenceur</p>
      </div>

      {/* Toggle mode */}
      <div className="flex gap-2 bg-[#18181B] border border-[#27272A] rounded-xl p-1">
        <button
          onClick={() => { setMode('username'); setError(null) }}
          className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 min-h-[44px] flex items-center justify-center gap-2 ${
            mode === 'username'
              ? 'bg-[#6366F1] text-white'
              : 'text-[#71717A] hover:text-[#A1A1AA]'
          }`}
        >
          <Search className="w-4 h-4" />
          Nom d'utilisateur
        </button>
        <button
          onClick={() => { setMode('screenshot'); setError(null) }}
          className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 min-h-[44px] flex items-center justify-center gap-2 ${
            mode === 'screenshot'
              ? 'bg-[#6366F1] text-white'
              : 'text-[#71717A] hover:text-[#A1A1AA]'
          }`}
        >
          <Camera className="w-4 h-4" />
          Capture d'ecran
        </button>
      </div>

      {/* Zone de saisie */}
      <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5">
        {mode === 'username' ? (
          <div className="space-y-5">
            {/* Plateforme */}
            <div>
              <label className="text-xs text-[#A1A1AA] font-medium mb-3 block">
                Plateforme
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => setPlatform('instagram')}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl border text-sm font-medium transition-all duration-200 min-h-[48px] ${
                    platform === 'instagram'
                      ? 'bg-[#E1306C]/10 border-[#E1306C]/30 text-[#E1306C]'
                      : 'bg-[#09090B] border-[#27272A] text-[#71717A] hover:border-[#3F3F46]'
                  }`}
                >
                  Instagram
                </button>
                <button
                  onClick={() => setPlatform('tiktok')}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl border text-sm font-medium transition-all duration-200 min-h-[48px] ${
                    platform === 'tiktok'
                      ? 'bg-[#FAFAFA]/5 border-[#FAFAFA]/20 text-[#FAFAFA]'
                      : 'bg-[#09090B] border-[#27272A] text-[#71717A] hover:border-[#3F3F46]'
                  }`}
                >
                  TikTok
                </button>
              </div>
            </div>

            {/* Username */}
            <div>
              <label className="text-xs text-[#A1A1AA] font-medium mb-3 block">
                Nom d'utilisateur
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[#71717A] text-base font-mono">@</span>
                <input
                  type="text"
                  inputMode="text"
                  autoCapitalize="none"
                  autoCorrect="off"
                  spellCheck="false"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="nom_utilisateur"
                  disabled={isAnalyzing}
                  className="w-full h-12 pl-10 pr-4 bg-[#09090B] border border-[#27272A] rounded-xl text-[#FAFAFA] placeholder-[#71717A] focus:outline-none focus:border-[#6366F1] transition-colors duration-200 font-mono text-base disabled:opacity-50"
                />
              </div>
            </div>
          </div>
        ) : (
          <ScreenshotUpload platform={platform} onResult={handleScreenshotResult} />
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-xl p-4">
          <AlertCircle className="w-5 h-5 text-[#EF4444] flex-shrink-0 mt-0.5" />
          <p className="text-sm text-[#EF4444]">{error}</p>
        </div>
      )}

      {/* Bouton Analyser */}
      {mode === 'username' && (
        <button
          onClick={handleAnalyze}
          disabled={!username.trim() || isAnalyzing}
          className="w-full h-12 rounded-xl font-semibold text-sm transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed bg-[#6366F1] hover:bg-[#818CF8] text-white flex items-center justify-center gap-2"
        >
          {isAnalyzing ? (
            <>
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" opacity="0.3" />
                <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
              </svg>
              Analyse en cours...
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              Analyser
            </>
          )}
        </button>
      )}
    </div>
  )
}

export default AnalyzePage
