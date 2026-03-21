import { Users } from 'lucide-react'

function DemographicsCard({ demographic }) {
  const d = demographic || {}

  const ageData = [
    { range: '13-17', value: d.age_13_17_pct || 0 },
    { range: '18-24', value: d.age_18_24_pct || 0 },
    { range: '25-34', value: d.age_25_34_pct || 0 },
    { range: '35-44', value: d.age_35_44_pct || 0 },
    { range: '45+', value: d.age_45_plus_pct || 0 },
  ]

  const male = d.estimated_male_pct || 0
  const female = d.estimated_female_pct || 0

  const topCountries = d.top_countries || []
  const topCities = d.top_cities || []

  const maxAge = Math.max(...ageData.map((a) => a.value), 1)

  return (
    <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5">
      <div className="flex items-center gap-2 mb-5">
        <Users className="w-4 h-4 text-[#6366F1]" />
        <h3 className="text-sm font-semibold text-[#FAFAFA]">Demographiques</h3>
      </div>

      {/* Age distribution */}
      <div className="mb-5">
        <p className="text-[10px] uppercase tracking-wider text-[#71717A] mb-3">Distribution d'age</p>
        <div className="space-y-2.5">
          {ageData.map((item) => (
            <div key={item.range} className="flex items-center gap-3">
              <span className="text-xs w-10 text-right text-[#71717A] font-mono flex-shrink-0">
                {item.range}
              </span>
              <div className="flex-1 h-4 rounded-md overflow-hidden bg-[#09090B]">
                <div
                  className="h-full rounded-md bg-[#6366F1] transition-all duration-700"
                  style={{ width: `${(item.value / maxAge) * 100}%`, minWidth: item.value > 0 ? '4px' : '0px' }}
                />
              </div>
              <span className="text-xs w-10 text-[#FAFAFA] font-mono flex-shrink-0">
                {item.value.toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Gender */}
      <div className="mb-5">
        <p className="text-[10px] uppercase tracking-wider text-[#71717A] mb-2">Genre</p>
        <div className="flex gap-0.5 h-4 rounded-md overflow-hidden">
          <div className="rounded-l-md bg-[#6366F1]" style={{ width: `${male}%` }} />
          <div className="rounded-r-md bg-[#EC4899]" style={{ width: `${female}%` }} />
        </div>
        <div className="flex justify-between mt-2">
          <span className="text-[10px] font-mono text-[#6366F1]">H {male.toFixed(0)}%</span>
          <span className="text-[10px] font-mono text-[#EC4899]">F {female.toFixed(0)}%</span>
        </div>
      </div>

      {/* Top locations */}
      {(topCountries.length > 0 || topCities.length > 0) && (
        <div>
          <p className="text-[10px] uppercase tracking-wider text-[#71717A] mb-3">Localisations</p>
          <div className="space-y-2">
            {topCountries.map((loc, i) => (
              <div key={i} className="flex justify-between text-xs">
                <span className="text-[#FAFAFA]">{loc.country || loc}</span>
                {loc.pct && <span className="font-mono text-[#A1A1AA]">{loc.pct}%</span>}
              </div>
            ))}
            {topCities.map((loc, i) => (
              <div key={`c-${i}`} className="flex justify-between text-xs">
                <span className="text-[#FAFAFA]">{loc.city || loc}</span>
                {loc.pct && <span className="font-mono text-[#A1A1AA]">{loc.pct}%</span>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default DemographicsCard
