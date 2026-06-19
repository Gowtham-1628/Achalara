#!/bin/bash

# Portfolio Management System - Backend Setup Script

set -e

echo "🚀 Setting up Portfolio Management System Backend"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version

# Create virtual environment
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Virtual environment created"
else
    echo "  Virtual environment already exists"
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create .env file if it doesn't exist
echo "✓ Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  Created .env file (edit with your configuration)"
else
    echo "  .env file already exists"
fi

# Check PostgreSQL
echo ""
echo "⚠️  Important: Make sure PostgreSQL is running"
echo "   To start PostgreSQL (if using Docker):"
echo "   docker run --name pms-db -e POSTGRES_PASSWORD=dev123 -e POSTGRES_DB=pms_dev -p 5432:5432 -d postgres:15"
echo ""

# Test database connection (optional)
echo "Testing database connection..."
if python3 -c "from app.db.database import engine; engine.connect(); print('✓ Database connection successful')" 2>/dev/null; then
    echo "✓ Database is ready"
else
    echo "⚠️  Database connection failed. Make sure PostgreSQL is running and .env is configured correctly."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Configure .env with your database credentials"
echo "3. Run server: uvicorn app.main:app --reload --port 8000"
echo "4. Visit: http://localhost:8000/docs"
echo ""
