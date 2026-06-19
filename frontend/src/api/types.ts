// Hand-typed from openapi.yaml — regenerate with `npm run gen:api` once backend is running

export type TradeAction = 'BUY' | 'SELL'

export interface ClientLogin { email: string; password: string }
export interface ClientCreate { name: string; email: string }
export interface ClientResponse {
  id: string; name: string; email: string
  created_at: string; updated_at: string
}

export interface AccountCreate { name: string; description?: string; account_number?: string | null }
export interface AccountResponse {
  id: string; client_id: string; name: string
  description: string; account_number: string | null
}

export interface SleeveCreate { strategy_id: string }
export interface SleeveResponse {
  id: string; account_id: string; strategy_id: string; strategy_name: string | null
}

export interface StrategyCreate { name: string; description?: string }
export interface StrategyResponse { id: string; name: string; description: string | null }

export interface TradeCreate {
  sleeve_id: string; trade_date: string; symbol: string
  action: TradeAction; quantity: number; price: number
  commission?: number; notes?: string
}
export interface TradeResponse extends TradeCreate { id: string; created_at: string }
export interface TradeSummary {
  id: string; sleeve_id: string; trade_date: string; symbol: string
  action: TradeAction; quantity: number; price: number
  commission: number; notes: string
}

export interface PerformanceSummary {
  mwr: number | null; twr: number | null
  total_invested: number; total_current_value: number
  start_date: string | null; end_date: string | null
}
export interface PerformanceChild { id: string; name: string; summary: PerformanceSummary }
export interface TimeseriesPoint { date: string; value: number }
export interface LevelPerformance {
  level: string; id: string; name: string
  summary: PerformanceSummary
  timeseries: TimeseriesPoint[]
  children: PerformanceChild[]
}

export interface MonthlyReturn { year: number; month: number; return: number }
export interface MonthlyReturnsResponse {
  level: string; id: string; name: string; monthly_returns: MonthlyReturn[]
}

export interface AggregatedPosition {
  symbol: string; quantity: number; cost_basis: number; avg_cost: number
  current_price: number | null; market_value: number | null
  unrealized_gain: number | null; unrealized_gain_pct: number | null
  trades_count: number
}
export interface ClientPositionsResponse {
  client_id: string; total_cost_basis: number; total_market_value: number
  total_unrealized_gain: number; positions_count: number
  positions: AggregatedPosition[]
}
export interface AccountPositionsResponse {
  account_id: string; total_cost_basis: number; total_market_value: number
  total_unrealized_gain: number; positions_count: number
  positions: AggregatedPosition[]
}

export interface PositionResponse {
  id: string; sleeve_id: string; symbol: string; quantity: number
  avg_cost: number; cost_basis: number; current_price: number | null
  market_value: number | null; unrealized_gain: number | null
  unrealized_gain_pct: number | null
}
export interface PortfolioSummary {
  total_cost_basis: number; total_market_value: number | null
  total_unrealized_gain: number | null
}
export interface PortfolioValueResponse {
  sleeve_id: string; summary: PortfolioSummary; positions: PositionResponse[]
}

export interface ClosedPosition {
  symbol: string; quantity: number; buy_date: string; sell_date: string
  cost_basis: number; proceeds: number; realized_gain: number; realized_gain_pct: number
}
export interface ClosedPositionsResponse {
  sleeve_id: string; total_realized_gain: number; positions: ClosedPosition[]
}

export interface ClientTradesResponse {
  client_id: string; total: number; skip: number; limit: number; trades: TradeSummary[]
}
export interface SleeveTradesResponse {
  sleeve_id: string; total: number; trades: TradeSummary[]
}

export interface MarketPriceUpdate { prices: Record<string, number> }

export interface FetchMarketPricesResponse {
  status: string; updated: number; failed: string[]
}

export interface ImportSummary {
  total_rows: number; valid_trades: number; duplicates_found: number; errors: number
  accounts_created?: number; strategies_created?: number; sleeves_created?: number
}
export interface ImportResponse {
  status: string; mode: string; routing: string
  summary: ImportSummary; message: string
  validation_warnings?: string[]; sync_log_id?: string
}

export interface SyncDailyResponse { status: string; message: string; trades_added: number }

export interface SyncLog {
  id: string; source: string; status: string; message: string
  trades_added: number; created_at: string
}
export interface SyncLogsResponse { total: number; skip: number; limit: number; logs: SyncLog[] }

export interface SheetSyncConfig {
  id: string; sleeve_id: string; sheet_id: string; range_name: string; enabled: boolean
}
export interface SyncConfigCreate {
  sleeve_id: string; sheet_id: string; range_name: string; enabled?: boolean
}
export interface SyncConfigUpdate { enabled: boolean }
