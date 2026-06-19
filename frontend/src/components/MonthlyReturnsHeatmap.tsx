import type { MonthlyReturn } from '@/api/types'

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

function cellColor(ret: number): string {
  if (ret > 0.05) return 'bg-gain text-paper'
  if (ret > 0.02) return 'bg-gain/60 text-summit-ink'
  if (ret > 0) return 'bg-gain/30 text-summit-ink'
  if (ret === 0) return 'bg-mist text-stone'
  if (ret > -0.02) return 'bg-loss/30 text-summit-ink'
  if (ret > -0.05) return 'bg-loss/60 text-paper'
  return 'bg-loss text-paper'
}

interface Props { monthlyReturns: MonthlyReturn[] }

export function MonthlyReturnsHeatmap({ monthlyReturns }: Props) {
  if (!monthlyReturns.length) {
    return (
      <div className="text-stone text-sm py-8 text-center">
        No monthly return data available.
      </div>
    )
  }

  const years = [...new Set(monthlyReturns.map((r) => r.year))].sort()
  const byYearMonth = new Map(
    monthlyReturns.map((r) => [`${r.year}-${r.month}`, r.return])
  )

  return (
    <div
      className="overflow-x-auto"
      aria-label="Monthly returns heatmap — each cell shows the return for that month"
    >
      <table className="text-xs font-mono min-w-full border-collapse">
        <thead>
          <tr>
            <th className="text-left text-stone pr-4 pb-2 font-normal">Year</th>
            {MONTHS.map((m) => (
              <th key={m} className="text-stone font-normal pb-2 px-1 text-center w-12">{m}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {years.map((year) => (
            <tr key={year}>
              <td className="text-stone pr-4 py-1">{year}</td>
              {MONTHS.map((_, idx) => {
                const ret = byYearMonth.get(`${year}-${idx + 1}`)
                return (
                  <td key={idx} className="py-1 px-0.5">
                    {ret != null ? (
                      <div
                        className={`rounded text-center py-1 px-0.5 tabular-nums ${cellColor(ret)}`}
                        title={`${MONTHS[idx]} ${year}: ${(ret * 100).toFixed(2)}%`}
                      >
                        {(ret * 100).toFixed(1)}%
                      </div>
                    ) : (
                      <div className="text-center text-stone/30 py-1">—</div>
                    )}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
