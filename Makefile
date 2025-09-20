.PHONY: help test lint format type-check coverage clean install-dev

# Python executable
PYTHON := python3

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-dev:  ## Install development dependencies
	$(PYTHON) -m pip install -r requirements-dev.txt

test:  ## Run tests
	$(PYTHON) -m pytest tests/ -v

coverage:  ## Run tests with coverage
	$(PYTHON) -m coverage run -m pytest tests/
	$(PYTHON) -m coverage report -m
	$(PYTHON) -m coverage html

lint:  ## Run linting checks
	$(PYTHON) -m flake8 src/

format:  ## Format code with black
	$(PYTHON) -m black src/

format-check:  ## Check if code is formatted correctly
	$(PYTHON) -m black --check src/

type-check:  ## Run type checking
	$(PYTHON) -m mypy src/ --ignore-missing-imports

fix-format:  ## Fix code formatting with black
	$(PYTHON) -m ruff format

ci:  ## Run all CI checks (format, lint, type-check, test)
	$(MAKE) format-check
	$(MAKE) lint
# $(MAKE) type-check
	$(MAKE) test

clean:  ## Clean up cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
