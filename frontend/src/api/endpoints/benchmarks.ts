import { apiClient } from '../client'
import type { BenchmarkResponse } from '../types'

const base = '/api/v1/benchmarks'

export const benchmarksApi = {
  getPerformance: (ticker: string, params?: { start_date?: string; end_date?: string }) =>
    apiClient
      .get<BenchmarkResponse>(`${base}/${ticker}/performance`, { params })
      .then((r) => r.data),
}
