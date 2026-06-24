# rich-raycast — Justfile
# https://github.com/casey/just

# List all available recipes (default)
default:
    @just --list

# Run the test suite
test:
    uv run pytest

# Run the test suite (alias)
t: test

# Run the linter
lint:
    uv run ruff check .

# Run the type checker
typecheck:
    uv run ty check

# Run the type checker (alias)
tc: typecheck

# Format all code
fmt:
    uv run ruff format .

# Format all code (alias)
format: fmt

# Auto-fix lint issues and format
fix:
    uv run ruff check . --fix
    uv run ruff format .

# Run all quality checks: lint, typecheck, and tests
check: lint typecheck test

# Sync dependencies from pyproject.toml
sync:
    uv sync

# Sync with dev dependencies
sync-dev:
    uv sync --group dev

# Build the package
build:
    uv build

# Run pre-commit hooks on all files
precommit:
    uv run pre-commit run --all-files

# Clean build artifacts and caches
clean:
    rm -rf dist/ build/ *.egg-info .pytest_cache .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name '*.pyc' -delete
