export function formatNumber(num) {
  if (num == null) return '0'
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
  }
  return num.toString()
}

export function formatPercentage(value, decimals = 1) {
  if (value == null) return '0%'
  return value.toFixed(decimals) + '%'
}

export function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function formatDateShort(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
  })
}

export function getScoreColor(score) {
  if (score == null) return '#A1A1AA'
  if (score <= 3) return '#EF4444'
  if (score <= 5) return '#EAB308'
  if (score <= 7) return '#6366F1'
  return '#22C55E'
}

export function getScoreLabel(score) {
  if (score == null) return 'N/A'
  if (score <= 3) return 'SUSPECT'
  if (score <= 5) return 'FAIBLE'
  if (score <= 7) return 'MOYEN'
  if (score <= 9) return 'BON'
  return 'EXCELLENT'
}
