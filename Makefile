#
# <!--
# <ai_agent_documentation>
#   <file_meta>
#     <name>Makefile</name>
#     <type>build_automation</type>
#     <purpose>Development, testing, release, and deployment automation (uv-based)</purpose>
#   </file_meta>
# </ai_agent_documentation>
# -->
# ArUCO Generator Makefile
# All Python tooling runs through uv (single source of truth: uv.lock)

.PHONY: help install install-dev format format-check lint typecheck audit \
	test unit-test integration test-ui test-api test-export test-quality \
	test-qa test-health coverage clean run dev check-deps db-init \
	pre-commit-install pre-commit validate ci requirements check-requirements \
	release deploy-preview deploy-prod validate-generation validate-export

RUN := uv run --

# Default target
help:
	@echo "ArUCO Generator - Make Commands"
	@echo "================================"
	@echo "make install            - Install runtime dependencies (uv sync --no-dev)"
	@echo "make install-dev        - Install dev dependencies (uv sync)"
	@echo "make format             - Format code with black + isort"
	@echo "make format-check       - Check formatting (black + isort)"
	@echo "make lint               - Check code style with flake8"
	@echo "make typecheck          - Run mypy type checks"
	@echo "make audit              - Security audit (bandit + pip-audit)"
	@echo "make test               - Run unit + integration + UI tests"
	@echo "make unit-test          - Run unit tests only"
	@echo "make test-api           - Run API integration tests"
	@echo "make test-health        - Run health endpoint checks"
	@echo "make test-ui            - Run UI smoke tests"
	@echo "make integration        - Run API + UI integration tests"
	@echo "make test-quality       - Run generation quality tests"
	@echo "make test-export        - Run export format tests"
	@echo "make test-qa            - Run all QA tests (quality + export)"
	@echo "make coverage           - Run tests with coverage report"
	@echo "make requirements       - Re-export requirements.txt from uv.lock"
	@echo "make check-requirements - Fail if requirements.txt is out of sync"
	@echo "make release VERSION=x.y.z - Bump all version locations + changelog"
	@echo "make deploy-preview     - Deploy a Vercel preview build"
	@echo "make deploy-prod        - Deploy to Vercel production (normally Git-driven)"
	@echo "make clean              - Remove cache and temporary files"
	@echo "make run                - Start the production server (gunicorn)"
	@echo "make dev                - Start the development server"
	@echo "make validate           - Run full validation suite"
	@echo "make ci                 - CI pipeline simulation"

# Install runtime dependencies only
install:
	@echo "Installing runtime dependencies..."
	uv sync --no-dev

# Install all dependencies including dev tools
install-dev:
	@echo "Installing development dependencies..."
	uv sync

# Run all tests
test: unit-test integration

# Run unit tests
unit-test:
	@echo "Running unit tests..."
	$(RUN) python -m pytest \
		tests/test_aruco_generator.py \
		tests/test_utils.py \
		tests/test_batch_generator.py \
		tests/test_calibration_logic.py \
		tests/test_charuco.py \
		tests/test_validation_metrics.py \
		tests/test_navigation.py \
		tests/test_security.py \
		-v

# Run API integration tests
test-api:
	@echo "Running API integration tests..."
	$(RUN) python -m pytest tests/test_api_endpoints.py tests/test_api.py -v

# Run health endpoint checks
test-health:
	@echo "Running health endpoint checks..."
	$(RUN) python -m pytest tests/test_api_endpoints.py -k health -v

# Run UI smoke tests
test-ui:
	@echo "Running UI smoke tests..."
	$(RUN) python -m pytest tests/test_ui_pages.py -v

# Run integration tests
integration: test-api test-ui

# Run generation quality tests
test-quality:
	@echo "Running generation quality tests..."
	$(RUN) python -m pytest tests/test_generation_quality.py -v

# Run export format tests
test-export:
	@echo "Running export format tests..."
	$(RUN) python -m pytest tests/test_export_formats.py tests/test_export_snapshots.py -v

# Run all quality assurance tests
test-qa: test-quality test-export
	@echo "All quality assurance tests passed!"

# Run tests with coverage
coverage:
	@echo "Running tests with coverage..."
	$(RUN) python -m pytest tests/ --cov=aruco_generator --cov=app --cov-report=html --cov-report=term --cov-report=xml --cov-fail-under=65

# Lint code
lint:
	@echo "Checking code style..."
	$(RUN) flake8 aruco_generator/ tests/ app.py api/ --max-line-length=88 --exclude=__pycache__ --ignore=E501,W503,E203

# Type checks (mypy config in pyproject.toml)
typecheck:
	@echo "Running mypy..."
	$(RUN) mypy aruco_generator/core aruco_generator/export

# Security audit: static analysis + known-vulnerability scan
audit:
	@echo "Running bandit..."
	$(RUN) bandit -r aruco_generator app.py api -ll --skip B101
	@echo "Running pip-audit against the lockfile export..."
	$(RUN) pip-audit -r requirements.txt --disable-pip

# Format code with black + isort
format:
	@echo "Formatting code..."
	$(RUN) black aruco_generator/ tests/ app.py api/ --line-length 88
	$(RUN) isort aruco_generator/ tests/ app.py api/ --profile black

# Format check (black + isort)
format-check:
	@echo "Checking formatting..."
	$(RUN) black --check aruco_generator/ tests/ app.py api/ --line-length 88
	$(RUN) isort --check-only aruco_generator/ tests/ app.py api/ --profile black

# Re-export the Vercel/Docker dependency manifest from the lockfile
requirements:
	uv export -q --no-header --no-dev --no-emit-project --format requirements-txt -o requirements.txt

# Fail if requirements.txt has drifted from uv.lock (CI gate)
check-requirements:
	@uv export -q --no-header --no-dev --no-emit-project --format requirements-txt -o /tmp/requirements.check.txt
	@diff -q requirements.txt /tmp/requirements.check.txt >/dev/null \
		|| (echo "requirements.txt is out of sync with uv.lock — run 'make requirements'" && exit 1)
	@echo "requirements.txt is in sync with uv.lock"

# Bump version across all tracked locations and scaffold the changelog
release:
	@test -n "$(VERSION)" || (echo "Usage: make release VERSION=x.y.z" && exit 1)
	$(RUN) python scripts/release.py $(VERSION)

# Clean cache and temporary files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f instance/*.db
	@echo "Cleanup complete!"

# Run production server
run:
	@echo "Starting production server on port 5000..."
	$(RUN) gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 2 app:app

# Run development server with auto-reload
dev:
	@echo "Starting development server with auto-reload..."
	$(RUN) gunicorn --bind 0.0.0.0:5000 --reload --log-level debug app:app

# Check for outdated dependencies
check-deps:
	@echo "Checking for outdated dependencies..."
	uv tree --outdated --depth 1

# Initialize database
db-init:
	@echo "Initializing database..."
	$(RUN) python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"

# Install and setup pre-commit hooks
pre-commit-install:
	@echo "Installing pre-commit hooks..."
	$(RUN) pre-commit install
	@echo "Pre-commit hooks installed successfully!"

# Run pre-commit checks manually
pre-commit:
	@echo "Running pre-commit checks..."
	$(RUN) pre-commit run --all-files

# Vercel deployments (production normally deploys via Git integration on main)
deploy-preview:
	vercel deploy --yes

deploy-prod:
	vercel deploy --prod --yes

# Quick validation of setup
validate: format-check lint typecheck test test-qa
	@echo "Validation complete! Code is clean and tests pass."

# Full CI/CD simulation with quality checks
ci: clean install-dev check-requirements format-check lint test test-qa coverage
	@echo "CI pipeline simulation complete!"

# Validate generation pipeline (no artifacts)
validate-generation:
	@echo "Validating generation pipeline..."
	$(RUN) python -m pytest tests/test_generation_quality.py::TestGenerationQuality::test_no_line_artifacts_in_single_marker -xvs
	$(RUN) python -m pytest tests/test_generation_quality.py::TestGenerationQuality::test_no_gaps_in_merged_rectangles -xvs
	$(RUN) python -m pytest tests/test_generation_quality.py::TestGenerationQuality::test_scaling_preserves_quality -xvs
	@echo "Generation pipeline validated - no artifacts detected!"

# Validate export formats
validate-export:
	@echo "Validating export formats..."
	$(RUN) python -m pytest tests/test_export_formats.py::TestSVGExport -xvs
	$(RUN) python -m pytest tests/test_export_formats.py::TestLightBurnExport -xvs
	$(RUN) python -m pytest tests/test_export_formats.py::TestExportConsistency -xvs
	@echo "Export formats validated successfully!"
