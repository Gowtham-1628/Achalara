import { useQuery } from '@tanstack/react-query'
import { benchmarksApi } from '@/api/endpoints/benchmarks'

export function useBenchmark(
  ticker: string,
  params?: { start_date?: string; end_date?: string },
) {
  return useQuery({
    queryKey: ['benchmark', ticker, params?.start_date, params?.end_date],
    queryFn: () => benchmarksApi.getPerformance(ticker, params),
    enabled: !!ticker,
    staleTime: 5 * 60 * 1000,
  })
}
