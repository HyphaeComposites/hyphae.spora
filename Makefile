# =============================================================================
# SPORA — Makefile
# Hyphae Composites
#
# Usage: make <target>
# Run `make help` to see all available commands.
# =============================================================================

# Load environment variables from .env if it exists
ifneq (,$(wildcard .env))
	include .env
	export
endif

PYTHON      := python3
PIP         := pip
PACKAGE     := spora
SCRIPTS     := scripts
TESTS       := tests
NOTEBOOKS   := notebooks
EXPORTS     := data/exports
DOCS        := docs/html

.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# help — list all targets with descriptions
# -----------------------------------------------------------------------------
.PHONY: help
help:
	@echo ""
	@echo "  SPORA — Hyphae Composites"
	@echo "  ─────────────────────────────────────────────────────"
	@echo "  make install          Install all Python dependencies"
	@echo "  make run-degradation  Run the RDKit degradation pipeline"
	@echo "  make run-ovito        Run the OVITO visualisation pipeline"
	@echo "  make test             Run the full pytest test suite"
	@echo "  make lint             Check code style with ruff"
	@echo "  make format           Auto-format code with black"
	@echo "  make export           Export results to CSV + Parquet"
	@echo "  make notebook         Launch Jupyter Lab"
	@echo "  make docs             Build HTML docs from docstrings"
	@echo "  make db-reset         Drop and recreate all Supabase tables"
	@echo "  make clean            Remove cached files and build artefacts"
	@echo "  ─────────────────────────────────────────────────────"
	@echo ""

# -----------------------------------------------------------------------------
# install — install all pinned dependencies
# -----------------------------------------------------------------------------
.PHONY: install
install:
	@echo "→ Upgrading pip..."
	$(PIP) install --upgrade pip
	@echo "→ Installing dependencies from requirements.txt..."
	$(PIP) install -r requirements.txt
	@echo "✓ Dependencies installed."

# -----------------------------------------------------------------------------
# run-degradation — run the RDKit degradation pipeline
# Pass arguments via ARGS: make run-degradation ARGS="--polymer PLA --mechanism hydrolysis"
# -----------------------------------------------------------------------------
.PHONY: run-degradation
run-degradation:
	@echo "→ Running degradation pipeline..."
	$(PYTHON) $(SCRIPTS)/run_degradation.py $(ARGS)

# -----------------------------------------------------------------------------
# run-ovito — run the OVITO visualisation pipeline
# Pass arguments via ARGS: make run-ovito ARGS="--run-label pla_hydro_60c_2pct --mode comparison"
# -----------------------------------------------------------------------------
.PHONY: run-ovito
run-ovito:
	@echo "→ Running OVITO visualisation pipeline..."
	$(PYTHON) $(SCRIPTS)/run_ovito.py $(ARGS)

# -----------------------------------------------------------------------------
# test — run the full pytest test suite with coverage
# -----------------------------------------------------------------------------
.PHONY: test
test:
	@echo "→ Running tests..."
	pytest $(TESTS)/ -v --cov=$(PACKAGE) --cov-report=term-missing
	@echo "✓ Tests complete."

# -----------------------------------------------------------------------------
# lint — check code style and catch common bugs with ruff
# -----------------------------------------------------------------------------
.PHONY: lint
lint:
	@echo "→ Linting with ruff..."
	ruff check $(PACKAGE)/ $(SCRIPTS)/
	@echo "✓ Lint complete."

# -----------------------------------------------------------------------------
# format — auto-format all Python files with black
# -----------------------------------------------------------------------------
.PHONY: format
format:
	@echo "→ Formatting with black..."
	black $(PACKAGE)/ $(SCRIPTS)/ $(TESTS)/
	@echo "✓ Formatting complete."

# -----------------------------------------------------------------------------
# export — export experiment results to CSV and Parquet
# -----------------------------------------------------------------------------
.PHONY: export
export:
	@echo "→ Exporting results to $(EXPORTS)/..."
	mkdir -p $(EXPORTS)
	$(PYTHON) $(SCRIPTS)/export_results.py --output-dir $(EXPORTS)
	@echo "✓ Export complete. Files are in $(EXPORTS)/"

# -----------------------------------------------------------------------------
# notebook — launch Jupyter Lab
# -----------------------------------------------------------------------------
.PHONY: notebook
notebook:
	@echo "→ Launching Jupyter Lab..."
	jupyter lab $(NOTEBOOKS)/

# -----------------------------------------------------------------------------
# docs — build HTML documentation from docstrings using pdoc
# -----------------------------------------------------------------------------
.PHONY: docs
docs:
	@echo "→ Building documentation..."
	mkdir -p $(DOCS)
	pdoc $(PACKAGE) --output-dir $(DOCS)
	@echo "✓ Docs built. Open $(DOCS)/index.html to view."

# -----------------------------------------------------------------------------
# db-reset — drop and recreate all Supabase tables from schema.sql
# This erases all stored experiment data. Export first with: make export
# -----------------------------------------------------------------------------
.PHONY: db-reset
db-reset:
	@echo "→ Resetting Supabase schema..."
	@echo "  This will drop and recreate all tables. Export data first if needed."
	@read -p "  Type YES to continue: " confirm && [ "$$confirm" = "YES" ] || (echo "Aborted." && exit 1)
	psql "$(DATABASE_URL)" -f $(PACKAGE)/db/schema.sql
	@echo "✓ Schema reset complete."

# -----------------------------------------------------------------------------
# clean — remove Python cache files and build artefacts
# -----------------------------------------------------------------------------
.PHONY: clean
clean:
	@echo "→ Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Clean complete."
