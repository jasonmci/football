.PHONY: help test lint format type-check coverage clean install-dev

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt

test:  ## Run tests
	python -m pytest tests/ -v

coverage:  ## Run tests with coverage
	python -m coverage run -m pytest tests/
	python -m coverage report -m
	python -m coverage html

lint:  ## Run linting checks
	python -m flake8 src/ tests/

format:  ## Format code with black
	python -m black src/ tests/

format-check:  ## Check if code is formatted correctly
	python -m black --check src/ tests/

type-check:  ## Run type checking
	python -m mypy src/ --ignore-missing-imports

ci:  ## Run all CI checks (format, lint, type-check, test)
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

clean:  ## Clean up cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
