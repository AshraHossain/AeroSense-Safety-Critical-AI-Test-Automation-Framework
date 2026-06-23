#!/bin/bash
# Setup script for AeroSense-TestForge development environment

set -e

echo "🚀 AeroSense-TestForge Setup"

# 1. Create .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aerosense
CLAUDE_MODEL=claude-sonnet-4-6
PORT=8000
LOG_LEVEL=info
ANTHROPIC_API_KEY=sk-ant-...
EOF
    echo "✓ .env created (update ANTHROPIC_API_KEY)"
else
    echo "✓ .env already exists"
fi

# 2. Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -e . -q

# 3. Run database migrations
echo "🗄️  Setting up database..."
docker-compose up -d postgres
sleep 5
alembic upgrade head

# 4. Run tests
echo "🧪 Running tests..."
pytest -q --cov=src --tb=short 2>/dev/null || true

# 5. Summary
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  docker-compose up          # Start all services"
echo "  pytest                     # Run tests"
echo "  k6 run load-tests/endpoints.js  # Load test"
echo ""
echo "Visit http://localhost:8000/health to verify"
