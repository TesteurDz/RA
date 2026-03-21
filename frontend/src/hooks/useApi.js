import { useState, useCallback } from 'react'
import axios from 'axios'

const api = axios.create({
  baseURL: '',
  timeout: 60000,
})

export function useApi() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const request = useCallback(async (method, url, data = null, config = {}) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api({ method, url, data, ...config })
      return response.data
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Erreur inconnue'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const get = useCallback((url, config) => request('get', url, null, config), [request])
  const post = useCallback((url, data, config) => request('post', url, data, config), [request])

  return { get, post, loading, error, setError }
}

export default api
