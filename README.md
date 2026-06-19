# PMS — Portfolio Management System

A multi-client, multi-strategy investment portfolio management backend. It tracks trades
through a **client → account → strategy** hierarchy, computes performance
(**MWR** and **TWR**), imports historical trades from CSV or Google Sheets, and fetches
market prices via the Webull API.

> **New here?** Read [CLAUDE.md](CLAUDE.md) for architecture and conventions,
> [ROADMAP.md](ROADMAP.md) for the phased plan, and [idea.md](idea.md) for the original vision.

## Tech stack

| Concern | Choice |
|---|---|
| API framework | FastAPI (sync `def` handlers, run in threadpool) |
| ORM | SQLAlchemy 2.0 — sync `Session` (not AsyncSession) |
| Migrations | Alembic |
| Database | PostgreSQL 15 (Docker); in-memory SQLite for tests |
| Cache / queue | Redis 7 (Docker) |
| Scheduler | APScheduler (`BackgroundScheduler`, daily Google Sheets sync) |
| Validation | Pydantic v2 |
| Tests / lint | pytest + httpx TestClient · Black · Flake8 |

## Repository layout

```
Achalara/
├── README.md            # You are here
├── CLAUDE.md            # Shared context (Sleeve model, monorepo layout)
├── openapi.yaml         # OpenAPI 3.0 spec — API contract between backend and frontend
├── ROADMAP.md           # Phase-by-phase plan
├── idea.md              # Project vision
├── backend/
│   ├── CLAUDE.md        # Backend conventions (FastAPI, SQLAlchemy, testing)
│   ├── app/             # FastAPI app: routes (thin) → services (logic) → models
│   ├── migrations/      # Alembic migrations
│   ├── tests/           # pytest suite (in-memory SQLite)
│   ├── bruno/           # Bruno API collection for manual/CLI testing
│   ├── docker-compose.yml   # Postgres + Redis
│   ├── infra.sh         # Stack manager (see INFRA.md)
│   ├── INFRA.md         # Infrastructure runbook
│   ├── GETTING_STARTED.md   # Step-by-step first-run guide
│   └── README.md        # Backend API reference
└── frontend/
    ├── CLAUDE.md        # Frontend conventions (React, TypeScript, API client)
    └── ...              # React + TypeScript app (Phase 5 — not yet scaffolded)
```

## Quick start

Requires [Homebrew](https://brew.sh), Python 3.10+, and a Docker runtime
(this repo was set up with [Colima](https://github.com/abiosoft/colima)).

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Start the whole stack (Docker runtime → Postgres+Redis → migrations → app):
./infra.sh up -d        # app on http://localhost:8000  (docs at /docs)
./infra.sh status       # check all layers
./infra.sh down         # stop everything
```

The app reads config from `backend/.env` (copy `backend/.env.example` to start).
`DATABASE_URL` points at the Dockerized Postgres by default. See
[backend/INFRA.md](backend/INFRA.md) for the full start/stop/restart/clean runbook and
[backend/GETTING_STARTED.md](backend/GETTING_STARTED.md) for a guided first run.

## Testing

```bash
cd backend && source venv/bin/activate

pytest                              # full suite (in-memory SQLite — no Docker needed)
pytest tests/test_admin.py          # a single file
pytest tests/test_admin.py -k sync  # filter by name

black app/ tests/ migrations/       # format
flake8 app/ --max-line-length=120   # lint
```

### API testing with Bruno

A complete [Bruno](https://www.usebruno.com/) collection lives in
[backend/bruno/](backend/bruno/) — a happy-path flow (client → account → strategy →
trades → prices → performance → admin) that auto-chains IDs between requests.

```bash
# GUI: open backend/bruno, pick the "Local" environment, Run Collection.
# CLI:
npm install -g @usebruno/cli
cd backend/bruno && bru run --env Local
```

## Open items / future work

- **Rotate the Webull API secrets** in `backend/.env` — they are live/valid and should not stay in a plaintext file long-term (keep only in the git-ignored `.env`).
- **Exercise the live Google Sheets sync** end-to-end — register a `SheetSyncConfig` and run `sync-daily`.
- **Decide symbol normalization** for exchange-prefixed tickers: trades store `BATS:IGE`; Webull lookups strip the prefix to `IGE`. Optionally normalize on import too.
- **Tech debt:** migrate Pydantic `class Config` → `model_config = ConfigDict(...)`; replace the Postgres-only `DISTINCT ON` in `twr_calculation.py`.
- **Frontend (Phase 5)** — React + TypeScript app. See [ROADMAP.md](ROADMAP.md) for the full plan.

## Conventions

- **Routes are thin** — all business logic lives in `app/services/`.
- **Sync everywhere** — plain `def` handlers + `Session`; no `async def` blocking calls.
- **Schema changes go through Alembic** (`alembic revision --autogenerate`).
- **Never bypass dedup** on trade imports, and **never hardcode secrets** — use `.env`.

See [CLAUDE.md](CLAUDE.md) for the complete list.
