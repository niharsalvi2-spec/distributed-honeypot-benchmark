.PHONY: help setup lint test deploy-single clean run-benchmarks

help:
	@echo "Distributed Honeypot Benchmark Framework"
	@echo "Available commands:"
	@echo "  make setup            Install dependencies and initialize environment"
	@echo "  make lint             Run code linters (black, flake8, mypy)"
	@echo "  make test             Execute test suite via pytest"
	@echo "  make deploy-single    Launch single-node baseline testbed"
	@echo "  make run-experiments Execute benchmark experimental test suite"
	@echo "  make clean            Clean temporary files, caches, and build artifacts"

setup:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

lint:
	black --check .
	flake8 . --max-line-length=120
	mypy benchmark collectors distributed correlation

test:
	pytest tests/ -v --cov=benchmark --cov=collectors --cov=distributed --cov=correlation

deploy-single:
	docker compose -f infrastructure/compose/single-node/docker-compose.yml up -d

run-experiments:
	python benchmark/runner.py --suite all

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
