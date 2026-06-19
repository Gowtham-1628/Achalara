# Portfolio Management System — Roadmap

## Phase 0: Foundation Setup ✅ COMPLETE

- [x] Directory structure, Git repo, `.gitignore`
- [x] Docker Compose for PostgreSQL + Redis
- [x] SQLAlchemy ORM models (Client, Account, Sleeve, Strategy, Trade, Position, SyncLog)
- [x] Alembic migration framework
- [x] Pydantic v2 schemas
- [x] FastAPI app with CORS middleware

---

## Phase 1: Foundation Validation ✅ COMPLETE

- [x] PostgreSQL connection verified
- [x] Alembic migrations running (`alembic upgrade head`)
- [x] FastAPI server starts clean; `/health` and `/docs` respond
- [x] pytest suite passing (SQLite in-memory)

---

## Phase 2: Historical Data Import ✅ COMPLETE

- [x] CSV import pipeline with `VALIDATE`/`IMPORT` modes
- [x] Auto-routing by Account + Strategy columns (creates sleeves as needed)
- [x] Duplicate detection on `(date, symbol, qty, price)` per sleeve
- [x] SyncLog audit trail per import
- [x] `GET /api/v1/admin/sync-logs`

---

## Phase 3: Portfolio Calculations ✅ COMPLETE

- [x] Position tracking: quantity-matched round-trips, weighted-avg cost basis
- [x] Open positions with unrealized P&L (Webull price fetch)
- [x] Closed positions with realized gains
- [x] MWR (IRR solver) and TWR (geometric linking) at sleeve / account / client / strategy level
- [x] Monthly return breakdown endpoint

---

## Phase 4: Daily Sync Pipeline ✅ COMPLETE

- [x] Public Google Sheets sync via CSV export (no credentials needed)
- [x] Dedup on `google_sheet_row_id` (safe to re-run)
- [x] APScheduler daily sync job (configurable hour via `.env`)
- [x] SheetSyncConfig CRUD — register sheet → sleeve mappings
- [x] `POST /api/v1/admin/sync-daily` and scheduler both call shared `run_daily_sync()`

---

## Phase 5: Frontend Application

- [ ] Initialize React + TypeScript app (Vite)
- [ ] API client (Axios/Fetch with typed responses from `openapi.yaml`)
- [ ] Client dashboard — list clients, create client, client detail
- [ ] Account & sleeve management views
- [ ] Performance dashboard — MWR/TWR charts, date range selector, strategy comparison
- [ ] Positions table (open + closed) with P&L columns
- [ ] Trade history view + manual trade entry form
- [ ] Admin tools — CSV import form, sync logs viewer, sync-config management

**Deliverable:** Full-featured web application for portfolio management.

---

## Phase 6: Advanced Features (Ongoing)

- [ ] **Auth** — JWT login, role-based access control, API key management
- [ ] **Reporting** — PDF/Excel export, performance attribution, benchmark comparison, tax-lot tracking
- [ ] **Real-time** — WebSocket for live price updates and position changes
- [ ] **Data quality** — anomaly detection, account reconciliation, audit logging
- [ ] **Performance optimization** — Redis caching for computed metrics, materialized views

---

## Open Technical Items

- Rotate the Webull API secrets in `backend/.env` — they are live and should move to a secrets manager long-term.
- Decide symbol normalization: trades store `BATS:IGE`; Webull lookups strip to `IGE`. Optionally normalize on import.
- Tech debt: migrate Pydantic `class Config` → `model_config = ConfigDict(...)`.
- Replace Postgres-only `DISTINCT ON` in `twr_calculation.py` for portability.
- Exercise live Google Sheets sync end-to-end once a `SheetSyncConfig` is registered.
