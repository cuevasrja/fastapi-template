set dotenv-load := true

# Show available commands
default:
    @just --list

# Install dependencies
install:
    pip install -r requirements-dev.txt

# Start development server
run:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start production server
serve:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Create a new Alembic migration (usage: just migrate-create "description")
migrate-create message:
    alembic revision --autogenerate -m "{{message}}"

# Apply pending migrations
migrate:
    alembic upgrade head

# Rollback last migration
migrate-rollback:
    alembic downgrade -1

# Show current migration
migrate-status:
    alembic current

# Show migration history
migrate-history:
    alembic history --verbose

# Start local PostgreSQL via Docker Compose
db-up:
    docker compose up -d db

# Stop local PostgreSQL
db-down:
    docker compose down

# Reset local database (destructive!)
db-reset:
    docker compose down -v
    docker compose up -d db

# Run tests
test:
    pytest -v

# Run tests with coverage
test-cov:
    pytest -v --cov=app --cov-report=term-missing

# Lint with ruff
lint:
    ruff check app/

# Format with ruff
format:
    ruff format app/

# Full quality check
check: lint
    ruff format --check app/

# Copy env example
env-setup:
    cp .env.example .env
    @echo ".env created — update SECRET_KEY before deploying!"
