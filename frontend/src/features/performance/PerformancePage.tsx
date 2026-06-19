import { useScope } from '@/context/ScopeContext'
import { useDateRange } from '@/context/DateRangeContext'
import { useClientPerformance, useClientMonthlyPerformance } from '@/hooks/useClients'
import { useAccountPerformance, useAccountMonthlyPerformance } from '@/hooks/useAccounts'
import { useSleevePerformance, useSleeveMonthlyPerformance } from '@/hooks/useSleeves'
import { useStrategyPerformance, useStrategyMonthlyPerformance } from '@/hooks/useStrategies'
import { PerformanceChart } from '@/components/PerformanceChart'
import { MonthlyReturnsHeatmap } from '@/components/MonthlyReturnsHeatmap'
import { LevelBreakdown } from '@/components/LevelBreakdown'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { SkeletonCard } from '@/components/Skeleton'
import { formatCurrency, formatPercent } from '@/lib/formatters'
import { useNavigate } from 'react-router-dom'
import type { LevelPerformance } from '@/api/types'

function PerformanceHero({ perf }: { perf: LevelPerformance }) {
  const { summary, level, name } = perf
  const gain = summary.total_current_value - summary.total_invested
  const gainPos = gain >= 0

  return (
    <div className="rounded-card p-8 bg-pine-deep text-paper mb-8 relative overflow-hidden">
      {/* Decorative contour lines — aria-hidden, purely decorative */}
      <svg
        aria-hidden="true"
        className="absolute inset-0 w-full h-full opacity-5 pointer-events-none"
        viewBox="0 0 400 200"
        preserveAspectRatio="xMidYMid slice"
      >
        {[20, 60, 100, 140, 180].map((y) => (
          <ellipse key={y} cx="200" cy={y} rx="380" ry="40" fill="none" stroke="white" strokeWidth="1" />
        ))}
      </svg>

      <div className="relative z-10">
        <p className="text-xs font-mono tracking-widest text-mist/60 uppercase mb-1">
          {level} · {name}
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6">
          <div>
            <p className="text-xs text-mist/60 mb-1">TWR</p>
            <p className={`font-mono text-3xl font-medium tabular-nums ${
              summary.twr != null && summary.twr >= 0 ? 'text-gain' : 'text-loss'
            }`}>
              {summary.twr != null ? formatPercent(summary.twr) : '—'}
            </p>
            <p className="text-xs text-mist/40 mt-0.5">Time Weighted</p>
          </div>
          <div>
            <p className="text-xs text-mist/60 mb-1">MWR</p>
            <p className={`font-mono text-3xl font-medium tabular-nums ${
              summary.mwr != null && summary.mwr >= 0 ? 'text-gain' : 'text-loss'
            }`}>
              {summary.mwr != null ? formatPercent(summary.mwr) : '—'}
            </p>
            <p className="text-xs text-mist/40 mt-0.5">Money Weighted</p>
          </div>
          <div>
            <p className="text-xs text-mist/60 mb-1">Current value</p>
            <p className="font-mono text-2xl text-paper tabular-nums">
              {formatCurrency(summary.total_current_value)}
            </p>
            <p className="text-xs text-mist/40 mt-0.5">
              vs {formatCurrency(summary.total_invested)} invested
            </p>
          </div>
          <div>
            <p className="text-xs text-mist/60 mb-1">Unrealised gain</p>
            <p className={`font-mono text-2xl tabular-nums ${gainPos ? 'text-gain' : 'text-loss'}`}>
              {formatCurrency(gain)}
            </p>
            <p className="text-xs text-mist/40 mt-0.5">
              {summary.twr != null && summary.mwr != null
                ? `TWR vs MWR: ${formatPercent(summary.twr - summary.mwr)}`
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

export function PerformancePage() {
  const { scope } = useScope()
  const navigate = useNavigate()
  const { data: perf, isLoading, isError, refetch } = useActivePerformance()
  const { data: monthly } = useActiveMonthly()

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

  const makeChildHref = (child: { id: string }) => {
    if (scope.level === 'client') return `/app/clients/${scope.clientId}/accounts/${child.id}`
    if (scope.level === 'account') return `/app/clients/${scope.clientId}/accounts/${scope.accountId}/sleeves/${child.id}`
    if (scope.level === 'strategy') return `/app/strategies/${scope.strategyId}`
    return '#'
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <PerformanceHero perf={perf} />

      {/* Timeseries chart */}
      <section className="bg-paper border border-stone/20 rounded-card p-6">
        <h2 className="text-sm font-mono uppercase tracking-wide text-stone mb-4">
          Portfolio value over time
        </h2>
        <PerformanceChart data={perf.timeseries} />
      </section>

      {/* Monthly heatmap */}
      {monthly && (
        <section className="bg-paper border border-stone/20 rounded-card p-6">
          <h2 className="text-sm font-mono uppercase tracking-wide text-stone mb-4">
            Month-on-month returns
          </h2>
          <MonthlyReturnsHeatmap monthlyReturns={monthly.monthly_returns} />
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
