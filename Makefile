# ArUCO Generator Makefile
# Automation for development, testing, and deployment

.PHONY: help install test unit-test integration-test lint format clean run dev check-deps coverage

# Default target
help:
	@echo "ArUCO Generator - Make Commands"
	@echo "================================"
	@echo "make install       - Install all dependencies"
	@echo "make install-dev   - Install development dependencies"
	@echo "make test          - Run all tests"
	@echo "make unit-test     - Run unit tests only"
	@echo "make integration   - Run integration tests only"
	@echo "make coverage      - Run tests with coverage report"
	@echo "make lint          - Check code style with flake8"
	@echo "make format        - Format code with black"
	@echo "make clean         - Remove cache and temporary files"
	@echo "make run           - Start the production server"
	@echo "make dev           - Start the development server"
	@echo "make check-deps    - Check for outdated dependencies"
	@echo "make db-init       - Initialize the database"

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	pip install -r <(grep -v '^\[' pyproject.toml | grep -E '^\s*"' | sed 's/[",]//g' | sed 's/^\s*//')

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install pytest pytest-cov pytest-flask black flake8 pre-commit bandit

# Run all tests
test: lint unit-test integration

# Run unit tests
unit-test:
	@echo "Running unit tests..."
	python -m pytest tests/test_aruco_generator.py -v

# Run integration tests
integration:
	@echo "Running integration tests..."
	python -m pytest tests/test_api_endpoints.py -v

# Run generation quality tests
test-quality:
	@echo "Running generation quality tests..."
	python -m pytest tests/test_generation_quality.py -v

# Run export format tests
test-export:
	@echo "Running export format tests..."
	python -m pytest tests/test_export_formats.py -v

# Run all quality assurance tests
test-qa: test-quality test-export
	@echo "All quality assurance tests passed!"

# Run tests with coverage
coverage:
	@echo "Running tests with coverage..."
	python -m pytest tests/ --cov=aruco_generator --cov=app --cov-report=html --cov-report=term

# Lint code
lint:
	@echo "Checking code style..."
	flake8 aruco_generator/ tests/ app.py --max-line-length=88 --exclude=__pycache__ --ignore=E501,W503

# Format code with black
format:
	@echo "Formatting code..."
	black aruco_generator/ tests/ app.py --line-length 88

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
	gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 2 main:app

# Run development server with auto-reload
dev:
	@echo "Starting development server with auto-reload..."
	gunicorn --bind 0.0.0.0:5000 --reload --log-level debug main:app

# Check for outdated dependencies
check-deps:
	@echo "Checking for outdated dependencies..."
	pip list --outdated

# Initialize database
db-init:
	@echo "Initializing database..."
	python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"

# Install and setup pre-commit hooks
pre-commit-install:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Pre-commit hooks installed successfully!"

# Run pre-commit checks manually
pre-commit:
	@echo "Running pre-commit checks..."
	pre-commit run --all-files

# Quick validation of setup
validate: lint unit-test test-qa
	@echo "Validation complete! Code is clean and tests pass."

# Full CI/CD simulation with quality checks
ci: clean install-dev lint test test-qa coverage
	@echo "CI pipeline simulation complete!"

# Validate generation pipeline (no artifacts)
validate-generation:
	@echo "Validating generation pipeline..."
	python -m pytest tests/test_generation_quality.py::TestGenerationQuality::test_no_line_artifacts_in_single_marker -xvs
	python -m pytest tests/test_generation_quality.py::TestGenerationQuality::test_no_gaps_in_merged_rectangles -xvs
	python -m pytest tests/test_generation_quality.py::TestGenerationQuality::test_scaling_preserves_quality -xvs
	@echo "Generation pipeline validated - no artifacts detected!"

# Validate export formats
validate-export:
	@echo "Validating export formats..."
	python -m pytest tests/test_export_formats.py::TestSVGExport -xvs
	python -m pytest tests/test_export_formats.py::TestLightBurnExport -xvs
	python -m pytest tests/test_export_formats.py::TestExportConsistency -xvs
	@echo "Export formats validated successfully!"

# Docker build (if needed in future)
docker-build:
	@echo "Building Docker image..."
	@echo "Docker support not yet implemented"

# Deploy (placeholder for future deployment automation)
deploy:
	@echo "Deployment automation not yet implemented"
	@echo "Use 'make run' for production server"
