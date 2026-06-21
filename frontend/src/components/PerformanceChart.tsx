import { useMemo } from 'react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts'
import type { BenchmarkPoint, TimeseriesPoint } from '@/api/types'
import { formatCurrency } from '@/lib/formatters'

interface Props {
  data: TimeseriesPoint[]
  benchmark?: BenchmarkPoint[]
  benchmarkTicker?: string
  label?: string
}

const MONTH_ABBR = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

function fmtAxisDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${MONTH_ABBR[d.getUTCMonth()]} '${String(d.getUTCFullYear()).slice(2)}`
}

function pickTicks(data: { date: string }[]): string[] {
  if (data.length <= 1) return data.map((d) => d.date)
  const first = new Date(data[0].date)
  const last = new Date(data[data.length - 1].date)
  const targetCount = Math.min(6, data.length)
  const ticks: string[] = []
  for (let i = 0; i < targetCount; i++) {
    const fraction = i / (targetCount - 1)
    const targetMs = first.getTime() + fraction * (last.getTime() - first.getTime())
    let best = data[0]
    let bestDiff = Infinity
    for (const pt of data) {
      const diff = Math.abs(new Date(pt.date).getTime() - targetMs)
      if (diff < bestDiff) { bestDiff = diff; best = pt }
    }
    if (!ticks.includes(best.date)) ticks.push(best.date)
  }
  return ticks
}

/**
 * For each portfolio date, find the closest benchmark bar on or before that date
 * and return its normalized value. This bridges the weekly benchmark frequency
 * gap against daily portfolio points.
 */
function interpolateBenchmark(
  portfolioDates: string[],
  benchmark: BenchmarkPoint[],
  startValue: number,
): (number | null)[] {
  if (!benchmark.length || !portfolioDates.length) return portfolioDates.map(() => null)

  const baseClose = benchmark[0].close
  // benchmark is sorted ascending
  const result: (number | null)[] = []

  for (const date of portfolioDates) {
    // binary search for the latest benchmark bar with date <= portfolio date
    let lo = 0
    let hi = benchmark.length - 1
    let match: BenchmarkPoint | null = null

    while (lo <= hi) {
      const mid = (lo + hi) >> 1
      if (benchmark[mid].date <= date) {
        match = benchmark[mid]
        lo = mid + 1
      } else {
        hi = mid - 1
      }
    }

    result.push(match ? (match.close / baseClose) * startValue : null)
  }

  return result
}

export function PerformanceChart({
  data,
  benchmark,
  benchmarkTicker = 'Benchmark',
  label = 'Portfolio value over time',
}: Props) {
  const chartData = useMemo(() => {
    if (!benchmark?.length || !data.length) return data as (TimeseriesPoint & { benchmark_value?: number | null })[]

    const benchmarkValues = interpolateBenchmark(
      data.map((pt) => pt.date),
      benchmark,
      data[0].value,
    )

    return data.map((pt, i) => ({ ...pt, benchmark_value: benchmarkValues[i] }))
  }, [data, benchmark])

  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-48 text-stone text-sm">
        No timeseries data available for this period.
      </div>
    )
  }

  const ticks = pickTicks(data)
  const hasBenchmark = benchmark && benchmark.length > 0

  return (
    <div aria-label={label}>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={chartData} margin={{ top: 4, right: 40, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#EAF0EC" />
          <XAxis
            dataKey="date"
            ticks={ticks}
            tickFormatter={fmtAxisDate}
            tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#8A968F' }}
            tickLine={false}
            axisLine={false}
            interval={0}
          />
          <YAxis
            tickFormatter={(v) => formatCurrency(v)}
            tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#8A968F' }}
            tickLine={false}
            axisLine={false}
            width={90}
          />
          <Tooltip
            formatter={(v: number, name: string) => [
              formatCurrency(v),
              name === 'benchmark_value' ? benchmarkTicker : 'Portfolio',
            ]}
            labelFormatter={fmtAxisDate}
            contentStyle={{
              fontFamily: 'IBM Plex Mono',
              fontSize: 12,
              border: '1px solid #EAF0EC',
              borderRadius: 8,
            }}
          />
          {hasBenchmark && (
            <Legend
              formatter={(value) => (value === 'benchmark_value' ? benchmarkTicker : 'Portfolio')}
              wrapperStyle={{ fontFamily: 'IBM Plex Mono', fontSize: 11, paddingTop: 8 }}
            />
          )}
          <Line
            type="monotone"
            dataKey="value"
            stroke="#2F5D4A"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#C9A24B' }}
          />
          {hasBenchmark && (
            <Line
              type="monotone"
              dataKey="benchmark_value"
              stroke="#C9A24B"
              strokeWidth={1.5}
              strokeDasharray="5 3"
              dot={false}
              activeDot={{ r: 4, fill: '#2F5D4A' }}
              connectNulls
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
