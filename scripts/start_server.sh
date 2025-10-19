#!/bin/bash
# Start MetricDuck MCP Server for local development
set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "MetricDuck MCP Server - Starting..."
echo "Project Root: $PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -e ."
    exit 1
fi

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Load environment variables if .env exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "📋 Loading environment variables from .env"
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
else
    echo "⚠️  No .env file found. Using default configuration."
    echo "   Copy .env.example to .env and configure API URL and key."
fi

# Start MCP server
echo "🚀 Starting MCP server..."
cd "$PROJECT_ROOT"
python -m metricduck_mcp
