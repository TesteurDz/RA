import { useEffect, useState } from 'react'
import { getScoreColor, getScoreLabel } from '../../utils/formatters'

function ScoreGauge({ score, size = 140 }) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const radius = (size - 16) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (animatedScore / 10) * circumference
  const color = getScoreColor(score)
  const label = getScoreLabel(score)
  const center = size / 2

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 200)
    return () => clearTimeout(timer)
  }, [score])

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#27272A"
            strokeWidth="8"
          />
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: 'stroke-dashoffset 1.2s ease-out' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-3xl font-bold font-mono"
            style={{ color }}
          >
            {score != null ? score.toFixed(1) : '--'}
          </span>
          <span className="text-[10px] text-[#71717A] mt-0.5">/10</span>
        </div>
      </div>
      <span
        className="text-[10px] font-bold font-mono uppercase tracking-widest px-3 py-1 rounded-lg"
        style={{
          color,
          backgroundColor: `${color}15`,
          border: `1px solid ${color}25`,
        }}
      >
        {label}
      </span>
    </div>
  )
}

export default ScoreGauge
