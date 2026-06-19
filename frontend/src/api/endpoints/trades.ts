import { apiClient } from '../client'
import type { TradeCreate, TradeResponse } from '../types'

export const tradesApi = {
  create: (body: TradeCreate) =>
    apiClient.post<TradeResponse>('/api/v1/trades/', body).then((r) => r.data),
}
