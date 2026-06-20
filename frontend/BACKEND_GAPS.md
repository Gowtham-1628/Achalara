# Backend Gaps

This file documents data the frontend needs that the current backend API does not expose.
Each entry includes: what the UI needs, the suggested endpoint + response shape, and which screen is blocked.

---

## 1. List all clients ✅ RESOLVED

`GET /api/v1/clients/` implemented. `ClientsPage` now uses the API list as the primary source;
`localStorage` is retained only for writing newly created/logged-in clients so they survive
a refresh when the API is temporarily unavailable.

---

## 2. Benchmark comparison

**UI need:** The Performance hero would benefit from a benchmark line (e.g. S&P 500) to contextualise MWR/TWR.
**Current workaround:** The hero shows MWR vs TWR and current value vs invested cost as the comparison — this is honest and available.
**Suggested endpoint:**
```
GET /api/v1/benchmarks/{ticker}/performance?start_date&end_date
-> { ticker, timeseries: [{ date, value }] }
```
**Blocked screen:** `PerformancePage` — `// BACKEND_GAP: benchmark` seam is in place.

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
