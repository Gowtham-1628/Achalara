# Portfolio Management System - Implementation Roadmap

## Phase 0: Foundation Setup ✅ COMPLETED

### Project Structure

- [x] Directory structure created
- [x] Git repository initialized (.gitignore configured)
- [x] Python virtual environment setup script created
- [x] Docker Compose for PostgreSQL + Redis

### Core Files

- [x] Database models (Client, Strategy, Trade, Position, SyncLog)
- [x] SQLAlchemy ORM with relationships
- [x] Alembic migration framework configured
- [x] Pydantic schemas for API validation
- [x] FastAPI application with CORS middleware

### Services

- [x] TradeValidator - CSV validation with Pydantic
- [x] GoogleSheetsService - API integration scaffold
- [x] PortfolioCalculation - Position calculations
- [x] MWRCalculation - Money Weighted Return algorithm
- [x] TWRCalculation - Time Weighted Return algorithm

### API Routes (Scaffolding)

- [x] Client routes (CRUD)
- [x] Strategy routes (CRUD)
- [x] Trade routes (CRUD)
- [x] Admin routes (import/sync)

### Documentation & Testing

- [x] README.md with quick start
- [x] GETTING_STARTED.md with detailed instructions
- [x] pytest configuration with fixtures
- [x] Sample validator tests

---

## Phase 1: Foundation Validation (Week 1) - TODO

### Database Setup

- [ ] Run setup.sh script
- [ ] Verify PostgreSQL connection
- [ ] Create initial Alembic migration
- [ ] Run database migration (alembic upgrade head)
- [ ] Verify tables created in PostgreSQL

### API Validation

- [ ] Start FastAPI server
- [ ] Test /health endpoint
- [ ] Create test client via API
- [ ] Verify Swagger UI (/docs)
- [ ] Test database persistence

### Local Testing

- [ ] Run pytest suite
- [ ] Verify test fixtures work
- [ ] Add more unit tests for validators
- [ ] Add integration tests for API routes

**Deliverable**: Working backend with database and basic API endpoints

---

## Phase 2: Historical Data Import (Week 2)

### CSV Import Pipeline

- [ ] Implement CSV parsing from file upload
- [ ] Build comprehensive trade validator
- [ ] Add duplicate detection logic
- [ ] Create reconciliation report UI
- [ ] Implement data persistence to database

### Google Sheets Integration

- [ ] Setup OAuth 2.0 credentials
- [ ] Implement Google Sheets API client
- [ ] Create sheet data fetcher
- [ ] Parse sheet data into trade objects
- [ ] Handle sheet API errors gracefully

### Import Audit Trail

- [ ] Implement SyncLog model persistence
- [ ] Track import success/failure
- [ ] Store validation errors
- [ ] Create import logs query endpoint
- [ ] Add import status monitoring

### Testing & Validation

- [ ] Create sample CSV test file
- [ ] Test VALIDATE mode endpoint
- [ ] Test IMPORT mode endpoint
- [ ] Verify no duplicates on re-import
- [ ] Test error handling and reporting

**Deliverable**: Can upload and import historical trades with validation

---

## Phase 3: Portfolio Calculations (Week 3)

### Position Calculation Enhancement

- [ ] Integrate position calculation service into API
- [ ] Add cost basis tracking per position
- [ ] Calculate weighted average cost
- [ ] Handle partial sales correctly
- [ ] Create position query endpoints

### Performance Metrics Integration

- [ ] Integrate MWR calculation into service layer
- [ ] Integrate TWR calculation into service layer
- [ ] Test with sample data
- [ ] Add edge case handling (no trades, single period, etc)
- [ ] Create performance query endpoints

### Real Price Data

- [ ] Add price source integration (placeholder)
- [ ] Implement current price fetching
- [ ] Calculate unrealized gains
- [ ] Create performance snapshot service
- [ ] Store daily snapshots

### API Endpoints

- [ ] GET /api/v1/clients/{client_id}/performance
- [ ] GET /api/v1/strategies/{strategy_id}/performance
- [ ] GET /api/v1/strategies/{strategy_id}/positions
- [ ] GET /api/v1/strategies/{strategy_id}/mwr
- [ ] GET /api/v1/strategies/{strategy_id}/twr

**Deliverable**: Real-time performance calculations and reporting

---

## Phase 4: Daily Sync Pipeline (Week 4)

### Google Sheets Daily Polling

- [ ] Implement scheduled daily sync task
- [ ] Query Google Sheet for new trades
- [ ] Parse and validate new trades
- [ ] Check for duplicates against existing
- [ ] Persist new trades to database

### Deduplication Strategy

- [ ] Implement row_id tracking from sheets
- [ ] Create duplicate detection logic
- [ ] Allow manual override of disputed trades
- [ ] Log deduplication decisions
- [ ] Prevent re-importing same trades

### Error Handling & Recovery

- [ ] Implement retry logic for failed syncs
- [ ] Create error notification system
- [ ] Build rollback mechanism for failed imports
- [ ] Create admin dashboard for sync monitoring
- [ ] Implement dry-run mode

### Scheduled Tasks

- [ ] Setup APScheduler for daily tasks
- [ ] Create background job runner
- [ ] Implement job status tracking
- [ ] Add admin endpoints to trigger/monitor jobs
- [ ] Create sync history reports

**Deliverable**: Automated daily data sync from Google Sheets

---

## Phase 5: Frontend Application (Week 5-6)

### React Setup

- [ ] Initialize React app (Create React App or Vite)
- [ ] Setup TypeScript
- [ ] Configure API client
- [ ] Setup routing

### Client Dashboard

- [ ] List all clients
- [ ] Create new client form
- [ ] Client detail page
- [ ] Edit client information

### Strategy Management

- [ ] List strategies for client
- [ ] Create strategy form
- [ ] Strategy detail page
- [ ] Edit strategy

### Performance Dashboard

- [ ] Display account-level performance
- [ ] Show strategy comparison
- [ ] Performance charts (MWR, TWR)
- [ ] Date range selector

### Position & Trade Views

- [ ] Current positions table
- [ ] Position details & history
- [ ] Trade transaction history
- [ ] Trade creation form

### Admin Tools

- [ ] Historical import form
- [ ] Sync logs viewer
- [ ] Import validation results
- [ ] Manual trade entry

**Deliverable**: Full-featured web application for portfolio management

---

## Phase 6: Advanced Features (Ongoing)

### Authentication & Authorization

- [ ] JWT token implementation
- [ ] User registration/login
- [ ] Role-based access control
- [ ] API key management

### Analytics & Reporting

- [ ] Custom date range reports
- [ ] Performance attribution
- [ ] Benchmark comparison
- [ ] Tax lot tracking
- [ ] Export to PDF/Excel

### Real-time Updates

- [ ] WebSocket for live updates
- [ ] Real-time position changes
- [ ] Price update feeds
- [ ] Trade execution alerts

### Data Quality

- [ ] Data validation rules engine
- [ ] Anomaly detection
- [ ] Account reconciliation
- [ ] Audit logging
- [ ] Data cleanup tools

### Performance Optimization

- [ ] Database query optimization
- [ ] Caching strategy (Redis)
- [ ] API response caching
- [ ] Materialized views for reports
- [ ] Background computation jobs

---

## Success Metrics

### Phase 1 Complete When:

- ✓ All tests passing
- ✓ API endpoints responding correctly
- ✓ Database connection stable

### Phase 2 Complete When:

- ✓ CSV import working with validation
- ✓ No duplicate trades on re-import
- ✓ Import logs tracking correctly

### Phase 3 Complete When:

- ✓ Performance calculations accurate
- ✓ MWR/TWR calculations verified
- ✓ Position data consistent

### Phase 4 Complete When:

- ✓ Daily sync running automatically
- ✓ Google Sheets data flowing in
- ✓ Zero duplicate issues

### Phase 5 Complete When:

- ✓ Users can manage portfolios via UI
- ✓ All API endpoints working via UI
- ✓ Performance charts displaying correctly

---

## Environment Variables Needed

```env
# Database
DATABASE_URL=postgresql://postgres:dev123@localhost:5432/pms_dev

# Google Sheets (for Phase 2+)
GOOGLE_SHEETS_API_KEY=<your_key>
GOOGLE_SHEETS_CREDENTIALS_FILE=./credentials.json

# Application
PYTHON_ENV=development
LOG_LEVEL=DEBUG
PORT=8000

# Optional (Phase 4+)
SCHEDULER_ENABLED=true
SYNC_SCHEDULE_HOUR=16  # 4 PM daily
```

---

## Technology Stack Summary

### Backend

- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL (relational DB)
- **ORM**: SQLAlchemy (Python ORM)
- **Migrations**: Alembic (database versioning)
- **Validation**: Pydantic (data validation)
- **Testing**: Pytest (unit & integration tests)
- **Task Scheduling**: APScheduler (background jobs)
- **API Docs**: Swagger/OpenAPI (auto-generated)

### Frontend (Phase 5)

- **Framework**: React 18+
- **Language**: TypeScript
- **State**: Redux/Zustand
- **Charts**: Recharts or Chart.js
- **HTTP**: Axios/Fetch
- **Styling**: Tailwind CSS or Material-UI
- **Build**: Vite or CRA

### Infrastructure

- **Database**: PostgreSQL 15
- **Cache**: Redis (optional)
- **Containers**: Docker & Docker Compose
- **Deployment**: AWS/GCP/Heroku (TBD)

---

## Current Status

**As of May 31, 2026:**

- ✅ Phase 0 COMPLETE - All scaffolding and foundation files created
- 🚀 Ready for Phase 1 - Start testing and validation

**Next Action**: Run `bash setup.sh` and start the server to validate Phase 0 completion.

---

## Files Ready to Work On

### For Phase 1 (This Week)

1. `backend/migrations/` - Create first migration
2. `backend/tests/test_*.py` - Add more tests
3. `backend/app/api/routes/` - Complete CRUD operations

### For Phase 2 (Next Week)

1. `backend/app/services/trade_ingestion.py` - Enhance validator
2. `backend/app/services/google_sheets_sync.py` - Complete implementation
3. `backend/app/api/routes/admin.py` - Implement import endpoints

### For Phase 3 (Following Week)

1. `backend/app/services/portfolio_calculation.py` - Enhance calculations
2. `backend/app/services/mwr_calculation.py` - Test thoroughly
3. `backend/app/services/twr_calculation.py` - Add more features

---

## Notes

- All services are modular and can be developed in parallel
- Tests should be added incrementally
- Database schema may need adjustments during development
- Google Sheets API credentials needed before Phase 2
- Consider Redis caching for performance metrics
