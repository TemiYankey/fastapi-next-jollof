# Backend Makefile
# Usage: make run, make test, make lint, etc.

.PHONY: run dev test lint format install clean help migrate migration db-init shell

# Default port (can be overridden: make run PORT=9000)
PORT ?= 8000

# Python
PYTHON := ./venv/bin/python
PIP := ./venv/bin/pip
PYTEST := ./venv/bin/pytest

help:
	@echo "Available commands:"
	@echo "  make install   - Create venv and install dependencies"
	@echo "  make run       - Start the server (PORT=8000)"
	@echo "  make dev       - Start with auto-reload (development)"
	@echo "  make test      - Run tests"
	@echo "  make coverage  - Run tests with coverage"
	@echo "  make lint      - Run linter (ruff)"
	@echo "  make format    - Format code (ruff)"
	@echo "  make clean     - Remove cache files"
	@echo "  make db-init   - Initialize database and create tables"
	@echo "  make migrate   - Apply pending migrations"
	@echo "  make migration - Create a new migration"
	@echo "  make shell     - Interactive Tortoise shell (IPython)"

install:
	python3 -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port $(PORT)

dev:
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port $(PORT) --reload

test:
	APP_ENV_FILE=.env.test $(PYTEST) tests/ -v

coverage:
	APP_ENV_FILE=.env.test $(PYTEST) tests/ -v --cov=app --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check app/ tests/

format:
	$(PYTHON) -m ruff format app/ tests/
	$(PYTHON) -m ruff check app/ tests/ --fix

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

db-init:
	$(PYTHON) -m tortoise init

migrate:
	$(PYTHON) -m tortoise migrate

migration:
	@read -p "Migration message: " msg; \
	$(PYTHON) -m tortoise makemigrations --name "$$msg"

shell:
	$(PYTHON) -m tortoise shell
