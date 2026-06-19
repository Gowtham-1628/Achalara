import { useState, type ReactNode } from 'react'

export interface Column<T> {
  key: string
  header: string
  render: (row: T) => ReactNode
  sortable?: boolean
  numeric?: boolean
}

interface Props<T> {
  columns: Column<T>[]
  rows: T[]
  getKey: (row: T) => string
  emptyMessage?: string
}

export function DataTable<T>({ columns, rows, getKey, emptyMessage = 'No data.' }: Props<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  if (!rows.length) {
    return <p className="text-stone text-sm py-8 text-center">{emptyMessage}</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-stone/20">
            {columns.map((col) => (
              <th
                key={col.key}
                className={`py-3 px-4 text-left text-xs font-mono uppercase tracking-wide text-stone font-normal
                  ${col.numeric ? 'text-right' : ''}
                  ${col.sortable ? 'cursor-pointer select-none hover:text-summit-ink' : ''}
                `}
                onClick={col.sortable ? () => handleSort(col.key) : undefined}
              >
                {col.header}
                {col.sortable && sortKey === col.key && (
                  <span className="ml-1">{sortDir === 'asc' ? '↑' : '↓'}</span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={getKey(row)}
              className="border-b border-stone/10 hover:bg-mist/50 transition-colors"
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={`py-3 px-4 font-mono text-summit-ink ${col.numeric ? 'text-right tabular-nums' : ''}`}
                >
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
