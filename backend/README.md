# Portfolio Management System - Backend

A FastAPI-based backend for managing investment portfolios, client accounts, strategies, and performance tracking.

## Features

- **Multi-Client Multi-Strategy Support**: Each client can have multiple accounts and investment strategies
- **Trade Ingestion**: Import trades from CSV or sync directly from a public Google Sheet
- **Position Tracking**: quantity-matched round-trips (each sell paired to a same-quantity buy), open/closed positions, realized & unrealized P&L, and real-time portfolio value
- **Performance Metrics**: Money Weighted Return (MWR) and Time Weighted Return (TWR)
- **Historical Analysis**: Track performance across custom date ranges
- **Deduplication**: Automatic duplicate detection on every import and sync
- **RESTful API**: Full OpenAPI documentation at `/docs`

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy 2.0 ORM
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Testing**: Pytest + httpx (SQLite in-memory)
- **Data Integration**: Public Google Sheets via CSV export (no credentials required)

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+

### Installation

1. **Create virtual environment**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Setup environment variables**

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL at minimum
```

4. **Create PostgreSQL database**

```bash
createdb pms_dev
```

5. **Run database migrations**

```bash
alembic upgrade head
```

6. **Start the server**

```bash
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000` — Swagger UI at `http://localhost:8000/docs`

## API Endpoints

### Clients

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/clients/` | Create client |
| `GET`  | `/api/v1/clients/{client_id}` | Get client |
| `GET`  | `/api/v1/clients/{client_id}/performance` | Aggregated MWR/TWR across all strategies |
| `GET`  | `/api/v1/clients/{client_id}/positions` | All positions merged across all strategies |
| `GET`  | `/api/v1/clients/{client_id}/trades` | All trades with pagination (`?skip=0&limit=100`) |

### Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/clients/{client_id}/accounts` | Create account |
| `GET`  | `/api/v1/clients/{client_id}/accounts` | List accounts |
| `GET`  | `/api/v1/clients/{client_id}/accounts/{account_id}` | Get account |

### Strategies

All strategy routes are nested under `/api/v1/clients/{client_id}/accounts/{account_id}/`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `.../strategies` | Create strategy |
| `GET`  | `.../strategies` | List strategies |
| `GET`  | `.../strategies/{strategy_id}/performance` | MWR/TWR (`?start_date=&end_date=`) |
| `GET`  | `.../strategies/{strategy_id}/positions` | Open positions with unrealized P&L |
| `GET`  | `.../strategies/{strategy_id}/positions/closed` | Closed positions with realized gains |
| `GET`  | `.../strategies/{strategy_id}/trades` | Trade history with pagination |
| `POST` | `.../strategies/{strategy_id}/market-prices` | Manually update prices |
| `POST` | `.../strategies/{strategy_id}/fetch-market-prices` | Fetch prices from Webull |

### Trades

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/trades/` | Create a single trade |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/admin/import-historical` | Import trades from CSV upload (`?mode=VALIDATE\|IMPORT`) |
| `POST` | `/api/v1/admin/sync-daily` | Sync trades from a public Google Sheet |
| `GET`  | `/api/v1/admin/sync-logs` | View import/sync audit logs |

## Google Sheets Integration

The sync-daily endpoint fetches data from any publicly shared Google Sheet (no API credentials needed).

**Sheet requirements:**
- Must be shared as "Anyone with the link can view"
- First row must be a header row with these columns: `Date`, `Symbol`, `Action`, `Quantity`, `Price`, `Commission`, `Strategy`, `Notes`
- `Date` can be `YYYY-MM-DD` or `YYYY/MM/DD` — both are normalized automatically
- `Action` can be `Buy`/`Sell` or `BUY`/`SELL` — case is normalized automatically

**Trade sheet:**

| Field | Value |
|-------|-------|
| Sheet ID | `12aXyVYCGtpmc44pBAdmKu7U6igT91cI93AT4vnJseM0` |
| Link | [Google Sheet](https://docs.google.com/spreadsheets/d/12aXyVYCGtpmc44pBAdmKu7U6igT91cI93AT4vnJseM0/edit?usp=drive_link) |
| Rows | 617 trades (Mar 2025 – May 2026) |
| Tab GID | `0` (first tab) |

**Example sync call:**

```bash
curl -X POST "http://localhost:8000/api/v1/admin/sync-daily" \
  -G \
  --data-urlencode "client_id=<your-client-id>" \
  --data-urlencode "strategy_id=<your-strategy-id>" \
  --data-urlencode "sheet_id=12aXyVYCGtpmc44pBAdmKu7U6igT91cI93AT4vnJseM0" \
  --data-urlencode "range_name=0"
```

Running the same sync twice is safe — duplicate trades are automatically skipped.

## CSV Import Format

When using `POST /api/v1/admin/import-historical`, the CSV must have these columns:

```
Date,Symbol,Action,Quantity,Price,Commission,Strategy,Notes
2025-03-17,FCG,BUY,41,24.28,0,Thematic ETFs,Initial purchase
```

Use `?mode=VALIDATE` first to dry-run without persisting, then `?mode=IMPORT` to persist.

## Testing

Run from the repo root (`pms/`):

```bash
# All tests
backend/venv/bin/pytest backend/tests -v

# With coverage
backend/venv/bin/pytest backend/tests --cov=backend/app

# Specific file
backend/venv/bin/pytest backend/tests/test_google_sheets.py -v

# Google Sheets integration tests only
backend/venv/bin/pytest backend/tests/test_google_sheets.py -v
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # Thin route handlers (clients, accounts, strategies, trades, admin)
│   │   └── schemas/         # Pydantic request/response models
│   ├── models/              # SQLAlchemy ORM models
│   ├── services/            # Business logic (MWR, TWR, portfolio calc, import, Webull, Sheets)
│   ├── db/                  # Database engine and session factory
│   ├── config.py            # Pydantic Settings (reads backend/.env)
│   └── main.py              # FastAPI app entry point
├── migrations/              # Alembic migration scripts
├── tests/                   # Test suite (46 tests)
├── requirements.txt
└── .env.example
```

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/pms_dev
WEBULL_APP_KEY=your_webull_key
WEBULL_APP_SECRET=your_webull_secret
PYTHON_ENV=development
LOG_LEVEL=DEBUG
PORT=8000
```

`GOOGLE_SHEETS_CREDENTIALS_FILE` is no longer needed — sheets are fetched publicly via CSV export.

## Development

- Format: `black app/`
- Lint: `flake8 app/`
- Schema changes: always use `alembic revision --autogenerate -m "description"`

## Next Steps

- [ ] Alembic initial migration (`alembic revision --autogenerate -m "initial schema"`)
- [ ] JWT authentication
- [ ] APScheduler for automated daily Google Sheets sync
- [ ] Redis job queue integration
- [ ] React frontend application
