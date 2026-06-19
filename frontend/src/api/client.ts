import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const apiClient = axios.create({ baseURL })

// Seam: add bearer token here when auth lands
// CONTRACT: no auth today — single-user mode per BACKEND_GAPS.md
apiClient.interceptors.request.use((config) => {
  // const token = getToken()
  // if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.detail ?? err.message ?? 'Unknown error'
    return Promise.reject(new Error(String(message)))
  }
)
