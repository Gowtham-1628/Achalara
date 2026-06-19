import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { strategiesApi } from '@/api/endpoints/strategies'
import type { StrategyCreate } from '@/api/types'

export const strategyKeys = {
  list: () => ['strategies'] as const,
  detail: (id: string) => ['strategies', id] as const,
  performance: (id: string, start?: string, end?: string) =>
    ['strategies', id, 'performance', start, end] as const,
  monthlyPerformance: (id: string) => ['strategies', id, 'performance', 'monthly'] as const,
}

export function useStrategies() {
  return useQuery({
    queryKey: strategyKeys.list(),
    queryFn: () => strategiesApi.list(),
  })
}

export function useStrategy(strategyId: string) {
  return useQuery({
    queryKey: strategyKeys.detail(strategyId),
    queryFn: () => strategiesApi.get(strategyId),
    enabled: !!strategyId,
  })
}

export function useStrategyPerformance(
  strategyId: string,
  params?: { start_date?: string; end_date?: string }
) {
  return useQuery({
    queryKey: strategyKeys.performance(strategyId, params?.start_date, params?.end_date),
    queryFn: () => strategiesApi.getPerformance(strategyId, params),
    enabled: !!strategyId,
  })
}

export function useStrategyMonthlyPerformance(strategyId: string) {
  return useQuery({
    queryKey: strategyKeys.monthlyPerformance(strategyId),
    queryFn: () => strategiesApi.getMonthlyPerformance(strategyId),
    enabled: !!strategyId,
  })
}

export function useCreateStrategy() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: StrategyCreate) => strategiesApi.create(body),
    onSuccess: () => qc.invalidateQueries({ queryKey: strategyKeys.list() }),
  })
}
