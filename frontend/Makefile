# Frontend Makefile
# Usage: make dev, make build, make test, etc.

.PHONY: dev build start test lint format install clean help

# Default port (can be overridden: make dev PORT=4000)
PORT ?= 3000

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make dev      - Start development server (PORT=3000)"
	@echo "  make build    - Build for production"
	@echo "  make start    - Start production server"
	@echo "  make test     - Run tests"
	@echo "  make coverage - Run tests with coverage"
	@echo "  make lint     - Run linter (eslint)"
	@echo "  make format   - Format code (prettier)"
	@echo "  make clean    - Remove cache and build files"

install:
	npm install

dev:
	npm run dev -- --port $(PORT)

build:
	npm run build

start:
	npm run start -- --port $(PORT)

test:
	npm run test:run

coverage:
	npm run test:coverage

lint:
	npm run lint

format:
	npx prettier --write "**/*.{ts,tsx,js,jsx,json,css,md}"

clean:
	rm -rf .next
	rm -rf node_modules/.cache
	rm -rf coverage
