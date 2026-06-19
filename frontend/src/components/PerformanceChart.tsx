import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts'
import type { TimeseriesPoint } from '@/api/types'
import { formatCurrency, formatDate } from '@/lib/formatters'

interface Props {
  data: TimeseriesPoint[]
  label?: string
}

export function PerformanceChart({ data, label = 'Portfolio value over time' }: Props) {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-48 text-stone text-sm">
        No timeseries data available for this period.
      </div>
    )
  }

  return (
    <div aria-label={label}>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#EAF0EC" />
          <XAxis
            dataKey="date"
            tickFormatter={(d) => formatDate(d)}
            tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#8A968F' }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tickFormatter={(v) => formatCurrency(v)}
            tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#8A968F' }}
            tickLine={false}
            axisLine={false}
            width={90}
          />
          <Tooltip
            formatter={(v: number) => [formatCurrency(v), 'Value']}
            labelFormatter={(l) => formatDate(l)}
            contentStyle={{
              fontFamily: 'IBM Plex Mono',
              fontSize: 12,
              border: '1px solid #EAF0EC',
              borderRadius: 8,
            }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#2F5D4A"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#C9A24B' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
