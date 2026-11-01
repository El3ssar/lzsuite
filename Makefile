.PHONY: help setup check test lint format build deps-backend deps-update

help:
	@echo "setup         Install locked dev environment and local hooks"
	@echo "check         Run lint, format checks, and tests"
	@echo "test          Run tests with coverage"
	@echo "lint          Check lint and formatting"
	@echo "format        Apply lint fixes and formatting"
	@echo "build         Build and validate wheel and source archive"
	@echo "deps-backend  Update lzcomplexity within its declared range"
	@echo "deps-update   Update all dependency locks within declared ranges"

setup:
	uv sync --locked
	uv run --no-sync pre-commit install --hook-type pre-commit --hook-type commit-msg

check: lint test

lint:
	uv run --locked ruff check .
	uv run --locked ruff format --check .

test:
	uv run --locked pytest --cov=lzsuite

format:
	uv run --locked ruff check . --fix
	uv run --locked ruff format .

build:
	uv build
	uv run --locked twine check dist/*

deps-backend:
	uv lock --upgrade-package lzcomplexity
	uv sync --locked

# Review the lockfile diff and run make check/build before committing updates.
deps-update:
	uv lock --upgrade
	uv sync --locked

.PHONY: docs docs-figures docs-serve

docs-figures:
	uv run --locked --group docs python scripts/generate_docs_figures.py
	uv run --locked --group docs python scripts/generate_social_card.py

docs: docs-figures
	uv run --locked --group docs pytest --doctest-modules src/lzsuite -q
	uv run --locked --group docs python scripts/check_documentation.py source
	uv run --locked --group docs mkdocs build --strict
	uv run --locked --group docs python scripts/check_documentation.py site

docs-serve:
	uv run --locked --group docs mkdocs serve --dev-addr 127.0.0.1:8000
