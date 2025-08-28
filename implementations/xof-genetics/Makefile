.PHONY: help install install-dev test test-cov lint format clean build publish

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=xof_genetics --cov-report=html --cov-report=term-missing

test-fast: ## Run fast tests only (skip slow tests)
	pytest tests/ -v -m "not slow"

test-limit: ## Run limit tests (large scale but not extreme)
	pytest tests/ -v -m "limit"

test-extreme: ## Run extreme server load tests
	pytest tests/ -v -m "extreme"

test-fill-resources: ## Run resource scaling tests
	pytest tests/ -v -m "fill_resources"

test-full-loop: ## Run full loop/soak tests
	pytest tests/ -v -m "full_loop"

test-all-extreme: ## Run all extreme tests (limit + extreme + fill_resources + full_loop)
	pytest tests/ -v -m "limit or extreme or fill_resources or full_loop"

lint: ## Run linting checks
	flake8 xof_genetics/ tests/
	mypy xof_genetics/

format: ## Format code with black
	black xof_genetics/ tests/

format-check: ## Check if code is formatted correctly
	black --check xof_genetics/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

publish: ## Publish to PyPI (requires twine)
	twine upload dist/*

demo: ## Run the demo
	python -m xof_genetics.demo

check: format-check lint test ## Run all checks (format, lint, test)

pre-commit: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files 