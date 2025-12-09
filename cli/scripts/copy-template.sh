#!/bin/bash
# Copy the project template to cli/template directory

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CLI_DIR="$ROOT_DIR/cli"
TEMPLATE_DIR="$CLI_DIR/template"

echo "Copying template from $ROOT_DIR to $TEMPLATE_DIR..."

# Clean existing template
rm -rf "$TEMPLATE_DIR"
mkdir -p "$TEMPLATE_DIR"

# Copy backend (excluding venv, __pycache__, etc.)
echo "Copying backend..."
rsync -av --exclude='venv' \
          --exclude='__pycache__' \
          --exclude='*.pyc' \
          --exclude='.pytest_cache' \
          --exclude='.coverage' \
          --exclude='htmlcov' \
          --exclude='.env' \
          --exclude='.env.local' \
          --exclude='*.db' \
          --exclude='*.sqlite3' \
          "$ROOT_DIR/backend/" "$TEMPLATE_DIR/backend/"

# Copy frontend (excluding node_modules, .next, etc.)
echo "Copying frontend..."
rsync -av --exclude='node_modules' \
          --exclude='.next' \
          --exclude='coverage' \
          --exclude='.env.local' \
          --exclude='.env.development.local' \
          --exclude='.env.production.local' \
          "$ROOT_DIR/frontend/" "$TEMPLATE_DIR/frontend/"

# Copy root files
echo "Copying root files..."
cp -f "$ROOT_DIR/.gitignore" "$TEMPLATE_DIR/" 2>/dev/null || true

echo "Template copied successfully!"
echo "Template size: $(du -sh "$TEMPLATE_DIR" | cut -f1)"
