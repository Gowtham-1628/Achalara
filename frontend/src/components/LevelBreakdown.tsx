import { Link } from 'react-router-dom'
import type { PerformanceChild } from '@/api/types'
import { formatCurrency } from '@/lib/formatters'
import { GainBadge } from './StatCard'

interface Props {
  children: PerformanceChild[]
  makeHref: (child: PerformanceChild) => string
  label: string
}

export function LevelBreakdown({ children, makeHref, label }: Props) {
  if (!children.length) {
    return <p className="text-stone text-sm py-6">No {label} to display.</p>
  }

  return (
    <div className="divide-y divide-stone/10">
      {children.map((child) => (
        <Link
          key={child.id}
          to={makeHref(child)}
          className="flex items-center justify-between py-4 px-2 hover:bg-mist/50 rounded transition-colors group"
        >
          <div>
            <p className="font-medium text-summit-ink group-hover:text-pine transition-colors">
              {child.name}
            </p>
            <p className="text-xs text-stone font-mono">
              {formatCurrency(child.summary.total_current_value)} invested value
            </p>
          </div>
          <div className="text-right space-y-0.5">
            <div className="flex gap-4 items-center justify-end">
              <div>
                <p className="text-xs text-stone">MWR</p>
                <GainBadge value={child.summary.mwr} />
              </div>
              <div>
                <p className="text-xs text-stone">TWR</p>
                <GainBadge value={child.summary.twr} />
              </div>
              <div>
                <p className="text-xs text-stone">Gain</p>
                <span className={`font-mono text-sm ${
                  (child.summary.total_current_value - child.summary.total_invested) >= 0
                    ? 'text-gain' : 'text-loss'
                }`}>
                  {formatCurrency(child.summary.total_current_value - child.summary.total_invested)}
                </span>
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  )
}
