# Getting Started - Portfolio Management System

## Prerequisites

- Python 3.10+
- Docker & Docker Compose (for PostgreSQL)
- Git

## Quick Start (5 minutes)

### Step 1: Navigate to Backend Directory

```bash
cd /Users/sai/Documents/Github\ 2/pms/backend
```

### Step 2: Run Setup Script

```bash
bash setup.sh
```

This will:

- Create Python virtual environment
- Install all dependencies
- Create .env file
- Check database connection

### Step 3: Start PostgreSQL with Docker

```bash
docker-compose up -d
```

Verify it's running:

```bash
docker ps
```

### Step 4: Activate Virtual Environment

```bash
source venv/bin/activate
```

### Step 5: Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

You should see:

```
Uvicorn running on http://127.0.0.1:8000
```

### Step 6: Open API Documentation

Visit: **http://localhost:8000/docs**

You'll see Swagger UI with all API endpoints documented and ready to test.

---

## Testing the API

### Create a Client

```bash
curl -X POST "http://localhost:8000/api/v1/clients/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Fund",
    "email": "fund@example.com"
  }'
```

### Create a Strategy

```bash
# Get client_id from previous response
curl -X POST "http://localhost:8000/api/v1/YOUR_CLIENT_ID/strategies" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Growth Portfolio",
    "description": "Aggressive growth strategy"
  }'
```

### Create a Trade

```bash
# Use strategy_id from previous response
curl -X POST "http://localhost:8000/api/v1/trades/" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "YOUR_STRATEGY_ID",
    "trade_date": "2026-05-15",
    "symbol": "AAPL",
    "action": "BUY",
    "quantity": 100,
    "price": 150.50,
    "commission": 10.00,
    "notes": "Initial purchase"
  }'
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app

# Run specific test file
pytest tests/test_validators.py
```

---

## Development Commands

### Format Code

```bash
black app/
```

### Lint Code

```bash
flake8 app/
```

### Initialize Alembic Migrations (if not done)

```bash
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Check Database Connection

```bash
python3 -c "from app.db.database import engine; print(engine.connect()); print('✓ Database connected')"
```

---

## Project Structure

```
pms/backend/
├── app/
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   │   ├── clients.py
│   │   │   ├── strategies.py
│   │   │   ├── trades.py
│   │   │   └── admin.py
│   │   └── schemas/         # Request/response models
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── client.py
│   │   ├── strategy.py
│   │   ├── trade.py
│   │   ├── position.py
│   │   └── sync_log.py
│   ├── services/            # Business logic
│   │   ├── trade_ingestion.py
│   │   ├── google_sheets_sync.py
│   │   ├── portfolio_calculation.py
│   │   ├── mwr_calculation.py
│   │   └── twr_calculation.py
│   ├── db/
│   │   └── database.py      # Database connection
│   ├── main.py              # FastAPI app entry point
│   └── config.py            # Configuration
├── tests/                   # Test suite
├── migrations/              # Alembic database migrations
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # PostgreSQL + Redis
├── .env                     # Environment variables
└── README.md               # Full documentation
```

---

## Environment Configuration

Edit `.env` to customize:

```env
DATABASE_URL=postgresql://postgres:dev123@localhost:5432/pms_dev
GOOGLE_SHEETS_API_KEY=your_api_key
GOOGLE_SHEETS_CREDENTIALS_FILE=./credentials.json
PYTHON_ENV=development
LOG_LEVEL=DEBUG
PORT=8000
```

---

## Stopping Services

### Stop the Server

```bash
# Press Ctrl+C in the terminal
```

### Stop PostgreSQL & Redis

```bash
docker-compose down
```

### Remove All Containers and Data (Fresh Start)

```bash
docker-compose down -v
```

---

## Troubleshooting

### PostgreSQL Connection Error

```
Error: could not connect to server: Connection refused
```

**Solution**: Make sure Docker is running and PostgreSQL is started

```bash
docker-compose up -d
docker ps  # Check if postgres is running
```

### Port Already in Use

```
Error: Address already in use
```

**Solution**: Change port or kill process using it

```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or find and kill process on 8000
lsof -i :8000
kill -9 <PID>
```

### Virtual Environment Issues

```bash
# Deactivate and reactivate
deactivate
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Module Import Errors

```bash
# Ensure you're in the correct directory
cd /Users/sai/Documents/Github\ 2/pms/backend

# Ensure venv is activated
source venv/bin/activate
```

---

## Next Phase: Historical Data Import

When ready to implement:

1. **Export Google Sheet as CSV**
   - File → Download → CSV

2. **Test Import Endpoint**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/admin/import-historical" \
     -H "accept: application/json" \
     -F "client_id=YOUR_CLIENT_ID" \
     -F "file=@path/to/trades.csv" \
     -F "mode=VALIDATE"
   ```

3. **If Validation Passes**
   ```bash
   # Change mode to IMPORT
   -F "mode=IMPORT"
   ```

---

## API Endpoints Reference

### Clients

- `POST /api/v1/clients` - Create client
- `GET /api/v1/clients/{client_id}` - Get client details
- `GET /api/v1/clients/{client_id}/performance` - Get performance
- `GET /api/v1/clients/{client_id}/positions` - Get all positions
- `GET /api/v1/clients/{client_id}/trades` - Get all trades

### Strategies

- `POST /api/v1/{client_id}/strategies` - Create strategy
- `GET /api/v1/{client_id}/strategies` - List strategies
- `GET /api/v1/{client_id}/strategies/{strategy_id}/performance` - Strategy performance
- `GET /api/v1/{client_id}/strategies/{strategy_id}/positions` - Strategy positions
- `GET /api/v1/{client_id}/strategies/{strategy_id}/trades` - Strategy trades

### Trades

- `POST /api/v1/trades` - Create trade

### Admin

- `POST /api/v1/admin/import-historical` - Import historical trades
- `POST /api/v1/admin/sync-daily` - Trigger daily sync
- `GET /api/v1/admin/sync-logs` - Get sync logs

---

## Need Help?

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Backend README**: Read backend/README.md
- **Check Logs**: uvicorn shows real-time logs when running

---

## Success Checklist ✓

- [ ] Docker is running
- [ ] PostgreSQL container is up
- [ ] Virtual environment is activated
- [ ] Server is running on :8000
- [ ] Can access http://localhost:8000/docs
- [ ] Can create a client via API
- [ ] Can create a strategy via API
- [ ] Can create a trade via API

**Once all checked, you're ready to start Phase 2: Historical Data Import!**
