import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { clientsApi } from '@/api/endpoints/clients'
import type { ClientCreate, ClientLogin } from '@/api/types'

export const clientKeys = {
  detail: (id: string) => ['clients', id] as const,
  performance: (id: string, start?: string, end?: string) =>
    ['clients', id, 'performance', start, end] as const,
  monthlyPerformance: (id: string) => ['clients', id, 'performance', 'monthly'] as const,
  positions: (id: string) => ['clients', id, 'positions'] as const,
  trades: (id: string, skip?: number, limit?: number) =>
    ['clients', id, 'trades', skip, limit] as const,
}

export function useClient(clientId: string) {
  return useQuery({
    queryKey: clientKeys.detail(clientId),
    queryFn: () => clientsApi.get(clientId),
    enabled: !!clientId,
  })
}

export function useClientPerformance(
  clientId: string,
  params?: { start_date?: string; end_date?: string }
) {
  return useQuery({
    queryKey: clientKeys.performance(clientId, params?.start_date, params?.end_date),
    queryFn: () => clientsApi.getPerformance(clientId, params),
    enabled: !!clientId,
  })
}

export function useClientMonthlyPerformance(clientId: string) {
  return useQuery({
    queryKey: clientKeys.monthlyPerformance(clientId),
    queryFn: () => clientsApi.getMonthlyPerformance(clientId),
    enabled: !!clientId,
  })
}

export function useClientPositions(clientId: string) {
  return useQuery({
    queryKey: clientKeys.positions(clientId),
    queryFn: () => clientsApi.getPositions(clientId),
    enabled: !!clientId,
  })
}

export function useClientTrades(clientId: string, skip = 0, limit = 100) {
  return useQuery({
    queryKey: clientKeys.trades(clientId, skip, limit),
    queryFn: () => clientsApi.getTrades(clientId, { skip, limit }),
    enabled: !!clientId,
  })
}

export function useLoginClient() {
  return useMutation({
    mutationFn: (body: ClientLogin) => clientsApi.login(body),
  })
}

export function useCreateClient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: ClientCreate) => clientsApi.create(body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }),
  })
}
