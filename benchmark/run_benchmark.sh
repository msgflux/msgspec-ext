#!/usr/bin/env bash
# Run benchmark with pydantic-settings available via uvx
# This avoids adding pydantic-settings as a project dependency

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running benchmark with pydantic-settings (via uvx)..."
echo

# Run the benchmark with both msgspec-ext (from current project) and pydantic-settings
cd "$SCRIPT_DIR" && uv run --with pydantic-settings --with pydantic python benchmark.py
