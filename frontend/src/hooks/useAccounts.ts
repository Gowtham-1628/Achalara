import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { accountsApi } from '@/api/endpoints/accounts'
import type { AccountCreate } from '@/api/types'

export const accountKeys = {
  list: (clientId: string) => ['accounts', clientId] as const,
  detail: (clientId: string, accountId: string) => ['accounts', clientId, accountId] as const,
  performance: (clientId: string, accountId: string, start?: string, end?: string) =>
    ['accounts', clientId, accountId, 'performance', start, end] as const,
  monthlyPerformance: (clientId: string, accountId: string) =>
    ['accounts', clientId, accountId, 'performance', 'monthly'] as const,
  positions: (clientId: string, accountId: string) =>
    ['accounts', clientId, accountId, 'positions'] as const,
}

export function useAccounts(clientId: string) {
  return useQuery({
    queryKey: accountKeys.list(clientId),
    queryFn: () => accountsApi.list(clientId),
    enabled: !!clientId,
  })
}

export function useAccount(clientId: string, accountId: string) {
  return useQuery({
    queryKey: accountKeys.detail(clientId, accountId),
    queryFn: () => accountsApi.get(clientId, accountId),
    enabled: !!clientId && !!accountId,
  })
}

export function useAccountPerformance(
  clientId: string,
  accountId: string,
  params?: { start_date?: string; end_date?: string }
) {
  return useQuery({
    queryKey: accountKeys.performance(clientId, accountId, params?.start_date, params?.end_date),
    queryFn: () => accountsApi.getPerformance(clientId, accountId, params),
    enabled: !!clientId && !!accountId,
  })
}

export function useAccountMonthlyPerformance(clientId: string, accountId: string) {
  return useQuery({
    queryKey: accountKeys.monthlyPerformance(clientId, accountId),
    queryFn: () => accountsApi.getMonthlyPerformance(clientId, accountId),
    enabled: !!clientId && !!accountId,
  })
}

export function useAccountPositions(clientId: string, accountId: string) {
  return useQuery({
    queryKey: accountKeys.positions(clientId, accountId),
    queryFn: () => accountsApi.getPositions(clientId, accountId),
    enabled: !!clientId && !!accountId,
  })
}

export function useCreateAccount() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ clientId, body }: { clientId: string; body: AccountCreate }) =>
      accountsApi.create(clientId, body),
    onSuccess: (_data, { clientId }) =>
      qc.invalidateQueries({ queryKey: accountKeys.list(clientId) }),
  })
}
