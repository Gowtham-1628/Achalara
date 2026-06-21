# Backend Gaps

This file documents data the frontend needs that the current backend API does not expose.
Each entry includes: what the UI needs, the suggested endpoint + response shape, and which screen is blocked.

---

## 1. List all clients ✅ RESOLVED

`GET /api/v1/clients/` implemented. `ClientsPage` now uses the API list as the primary source;
`localStorage` is retained only for writing newly created/logged-in clients so they survive
a refresh when the API is temporarily unavailable.

---

## 2. Benchmark comparison ✅ RESOLVED

`GET /api/v1/benchmarks/{ticker}/performance` implemented. Returns `{ ticker, timeseries: [{date, close}], warning }`.
- Portfolio Value chart shows a normalized benchmark line (gold dashed) overlaid on portfolio value.
- TWR vs MWR returns chart shows a third line for benchmark cumulative return (clay dashed).
- Ticker selector on PerformancePage: SPY/QQQ/AGG/DIA quick buttons + free-text input (debounced 500ms).
- Graceful: if Webull keys absent, returns `timeseries: []` with `warning` — charts render without benchmark line.

---

## 3. Authentication / multi-user

**UI need:** Login, session management, user accounts.
**Current workaround:** Single-user mode. The Axios client has an interceptor seam at `src/api/client.ts` (commented out) where a bearer token can be injected.
**Suggested:** OAuth2 / JWT via a `/api/v1/auth/` namespace.
**Blocked screen:** `SettingsPage` — placeholder shown.

---

## 4. Strategy-level sleeve listing ✅ RESOLVED

`account_id` and `client_id` are now included in `PerformanceChild` when the parent level is `strategy`.
`PerformancePage.makeChildHref` uses them to build the full sleeve URL
(`/app/clients/{client_id}/accounts/{account_id}/sleeves/{sleeve_id}`) when they are present.

---

## 5. Sync log filtering by sleeve

**UI need:** The Imports page would benefit from filtering sync logs by sleeve, not just client.
**Suggested endpoint extension:**
```
GET /api/v1/admin/sync-logs?client_id=&sleeve_id=&skip=&limit=
```
**Blocked screen:** `ImportsPage` — currently shows all logs for a client.
