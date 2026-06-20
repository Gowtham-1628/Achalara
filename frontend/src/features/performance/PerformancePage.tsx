import { useScope } from '@/context/ScopeContext'
import { useDateRange } from '@/context/DateRangeContext'

const PRESETS = [
  { label: '1M',  months: 1 },
  { label: '3M',  months: 3 },
  { label: '6M',  months: 6 },
  { label: '1Y',  months: 12 },
  { label: '3Y',  months: 36 },
  { label: 'MAX', months: null },
] as const

function toISODate(d: Date): string {
  return d.toISOString().slice(0, 10)
}
import { useClientPerformance, useClientMonthlyPerformance, useClientReturnsSeries } from '@/hooks/useClients'
import { useAccountPerformance, useAccountMonthlyPerformance, useAccountReturnsSeries } from '@/hooks/useAccounts'
import { useSleevePerformance, useSleeveMonthlyPerformance, useSleeveReturnsSeries } from '@/hooks/useSleeves'
import { useStrategyPerformance, useStrategyMonthlyPerformance, useStrategyReturnsSeries } from '@/hooks/useStrategies'
import { PerformanceChart } from '@/components/PerformanceChart'
import { ReturnsSeriesChart } from '@/components/ReturnsSeriesChart'
import { MonthlyReturnsHeatmap } from '@/components/MonthlyReturnsHeatmap'
import { LevelBreakdown } from '@/components/LevelBreakdown'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { SkeletonCard } from '@/components/Skeleton'
import { formatCurrency, formatPercent } from '@/lib/formatters'
import { useNavigate } from 'react-router-dom'
import type { LevelPerformance, PerformanceChild } from '@/api/types'

function PerformanceHero({ perf }: { perf: LevelPerformance }) {
  const { summary, level, name } = perf
  const gainPos = (summary.total_unrealized_gain ?? 0) >= 0

  return (
    <div className="rounded-card p-8 bg-pine-deep text-paper mb-8">
      <div>
        <p className="text-xs font-mono tracking-widest text-mist/60 uppercase mb-1">
          {level} · {name}
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6">
          <div>
            <p className="text-xs text-mist/60 mb-1">TWR</p>
            <p className={`font-mono text-3xl font-medium tabular-nums ${
              summary.twr_pct != null && summary.twr_pct >= 0 ? 'text-gain' : 'text-loss'
            }`}>
              {summary.twr_pct != null ? formatPercent(summary.twr_pct) : '—'}
            </p>
            <p className="text-xs text-mist/40 mt-0.5">Time Weighted</p>
          </div>
          <div>
            <p className="text-xs text-mist/60 mb-1">MWR</p>
            <p className={`font-mono text-3xl font-medium tabular-nums ${
              summary.mwr_pct != null && summary.mwr_pct >= 0 ? 'text-gain' : 'text-loss'
            }`}>
              {summary.mwr_pct != null ? formatPercent(summary.mwr_pct) : '—'}
            </p>
            <p className="text-xs text-mist/40 mt-0.5">Money Weighted</p>
          </div>
          <div>
            <p className="text-xs text-mist/60 mb-1">Market value</p>
            <p className="font-mono text-2xl text-paper tabular-nums">
              {formatCurrency(summary.total_market_value)}
            </p>
            <p className="text-xs text-mist/40 mt-0.5">
              {formatCurrency(summary.total_cost_basis)} cost basis
            </p>
          </div>
          <div>
            <p className="text-xs text-mist/60 mb-1">Unrealised gain</p>
            <p className={`font-mono text-2xl tabular-nums ${gainPos ? 'text-gain' : 'text-loss'}`}>
              {formatCurrency(summary.total_unrealized_gain)}
            </p>
            <p className="text-xs text-mist/40 mt-0.5">
              {summary.twr_pct != null && summary.mwr_pct != null
                ? `TWR vs MWR: ${formatPercent(summary.twr_pct - summary.mwr_pct)}`
                : 'Since inception'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function useActivePerformance() {
  const { scope } = useScope()
  const { startDate, endDate } = useDateRange()
  const dateParams = { start_date: startDate, end_date: endDate }

  const client = useClientPerformance(scope.clientId ?? '', dateParams)
  const account = useAccountPerformance(
    scope.clientId ?? '', scope.accountId ?? '', dateParams
  )
  const sleeve = useSleevePerformance(
    scope.clientId ?? '', scope.accountId ?? '', scope.sleeveId ?? '', dateParams
  )
  const strategy = useStrategyPerformance(scope.strategyId ?? '', dateParams)

  if (scope.level === 'sleeve') return sleeve
  if (scope.level === 'account') return account
  if (scope.level === 'strategy') return strategy
  if (scope.level === 'client') return client
  return { data: undefined, isLoading: false, isError: false, refetch: () => {} }
}

function useActiveMonthly() {
  const { scope } = useScope()
  const client = useClientMonthlyPerformance(scope.clientId ?? '')
  const account = useAccountMonthlyPerformance(scope.clientId ?? '', scope.accountId ?? '')
  const sleeve = useSleeveMonthlyPerformance(scope.clientId ?? '', scope.accountId ?? '', scope.sleeveId ?? '')
  const strategy = useStrategyMonthlyPerformance(scope.strategyId ?? '')

  if (scope.level === 'sleeve') return sleeve
  if (scope.level === 'account') return account
  if (scope.level === 'strategy') return strategy
  if (scope.level === 'client') return client
  return { data: undefined, isLoading: false, isError: false }
}

function useActiveReturnsSeries() {
  const { scope } = useScope()
  const client = useClientReturnsSeries(scope.clientId ?? '')
  const account = useAccountReturnsSeries(scope.clientId ?? '', scope.accountId ?? '')
  const sleeve = useSleeveReturnsSeries(scope.clientId ?? '', scope.accountId ?? '', scope.sleeveId ?? '')
  const strategy = useStrategyReturnsSeries(scope.strategyId ?? '')

  if (scope.level === 'sleeve') return sleeve
  if (scope.level === 'account') return account
  if (scope.level === 'strategy') return strategy
  if (scope.level === 'client') return client
  return { data: undefined }
}

export function PerformancePage() {
  const { scope } = useScope()
  const navigate = useNavigate()
  const { startDate, endDate, setDateRange } = useDateRange()
  const { data: perf, isLoading, isError, refetch } = useActivePerformance()
  const { data: monthly } = useActiveMonthly()
  const { data: returnsSeries } = useActiveReturnsSeries()

  const applyPreset = (months: number | null) => {
    if (months === null) {
      setDateRange(undefined, undefined)
    } else {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - months)
      setDateRange(toISODate(start), toISODate(end))
    }
  }

  const activePreset = (() => {
    if (!startDate && !endDate) return 'MAX'
    const end = endDate ? new Date(endDate) : new Date()
    const start = startDate ? new Date(startDate) : null
    if (!start) return null
    const diffMonths = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth())
    const match = PRESETS.find((p) => p.months === diffMonths)
    return match?.label ?? null
  })()

  if (!scope.level) {
    return (
      <EmptyState
        title="Select a client or strategy"
        message="Choose a client from the Clients tab to view their performance, or browse Strategies to see firm-wide roll-ups."
        action={{ label: 'Browse clients', onClick: () => navigate('/app/clients') }}
      />
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    )
  }

  if (isError || !perf) {
    return <ErrorState message="Could not load performance data." onRetry={() => refetch()} />
  }

  const makeChildHref = (child: PerformanceChild) => {
    if (scope.level === 'client') return `/app/clients/${scope.clientId}/accounts/${child.id}`
    if (scope.level === 'account') return `/app/clients/${scope.clientId}/accounts/${scope.accountId}/sleeves/${child.id}`
    if (scope.level === 'strategy' && child.client_id && child.account_id) {
      // account_id and client_id are populated on strategy children so we can link directly to the sleeve
      return `/app/clients/${child.client_id}/accounts/${child.account_id}/sleeves/${child.id}`
    }
    if (scope.level === 'strategy') return `/app/strategies/${scope.strategyId}`
    return '#'
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <PerformanceHero perf={perf} />

      {/* Timeseries chart */}
      <section className="bg-paper border border-stone/20 rounded-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-mono uppercase tracking-wide text-stone">
            Portfolio value over time
          </h2>
          <div className="flex gap-1">
            {PRESETS.map((p) => (
              <button
                key={p.label}
                onClick={() => applyPreset(p.months)}
                className={`px-2.5 py-1 text-xs font-mono rounded transition-colors ${
                  activePreset === p.label
                    ? 'bg-pine text-paper'
                    : 'text-stone hover:text-summit-ink hover:bg-mist'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
        <PerformanceChart data={perf.timeseries.filter((pt) => {
          if (startDate && pt.date < startDate) return false
          if (endDate && pt.date > endDate) return false
          return true
        })} />
      </section>

      {/* TWR vs MWR returns series */}
      {returnsSeries && returnsSeries.series.length > 0 && (
        <section className="bg-paper border border-stone/20 rounded-card p-6">
          <div className="flex items-center justify-between mb-1">
            <h2 className="text-sm font-mono uppercase tracking-wide text-stone">
              TWR vs MWR — cumulative returns
            </h2>
            <div className="flex gap-4 text-xs font-mono text-stone">
              <span className="flex items-center gap-1.5">
                <span className="inline-block w-6 border-t-2 border-pine" />
                TWR
              </span>
              <span className="flex items-center gap-1.5">
                <span className="inline-block w-6 border-t-2 border-dashed border-gold" />
                MWR
              </span>
            </div>
          </div>
          <p className="text-xs text-stone/60 mb-4">
            Weekly snapshots since inception · solid = time-weighted · dashed = money-weighted
          </p>
          <ReturnsSeriesChart data={returnsSeries.series.filter((pt) => {
            if (startDate && pt.date < startDate) return false
            if (endDate && pt.date > endDate) return false
            return true
          })} />
        </section>
      )}

      {/* Monthly heatmap */}
      {monthly && (
        <section className="bg-paper border border-stone/20 rounded-card p-6">
          <h2 className="text-sm font-mono uppercase tracking-wide text-stone mb-4">
            Month-on-month returns
          </h2>
          <MonthlyReturnsHeatmap monthlyReturns={monthly.months} />
        </section>
      )}

      {/* Level breakdown */}
      {perf.children.length > 0 && (
        <section className="bg-paper border border-stone/20 rounded-card p-6">
          <h2 className="text-sm font-mono uppercase tracking-wide text-stone mb-4">
            {scope.level === 'client' ? 'Accounts' : scope.level === 'account' ? 'Sleeves' : 'Breakdown'}
          </h2>
          <LevelBreakdown
            children={perf.children}
            makeHref={makeChildHref}
            label={scope.level === 'client' ? 'accounts' : 'sleeves'}
          />
        </section>
      )}
    </div>
  )
}
