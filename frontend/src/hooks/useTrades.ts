import { useMutation, useQueryClient } from '@tanstack/react-query'
import { tradesApi } from '@/api/endpoints/trades'
import type { TradeCreate } from '@/api/types'
import { sleeveKeys } from './useSleeves'

export function useCreateTrade() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: TradeCreate) => tradesApi.create(body),
    onSuccess: (_data, variables) => {
      // We don't have clientId/accountId here — invalidate broadly by sleeve pattern
      qc.invalidateQueries({ predicate: (q) => q.queryKey.includes(variables.sleeve_id) })
      qc.invalidateQueries({ queryKey: sleeveKeys.list('', '') })
    },
  })
}
