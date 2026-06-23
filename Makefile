.PHONY: help install test coverage lint format typecheck security setup docker-up docker-down load-test chaos-test clean

help:
	@echo "AeroSense-TestForge Make Targets"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e . -q

setup: ## Setup development environment
	bash scripts/setup.sh

test: ## Run unit tests (no postgres required)
	pytest -k "not integration" --cov=src --cov-report=term-missing

test-all: ## Run all tests (requires postgres)
	pytest --cov=src --cov-report=term-missing

integration-test: ## Run integration tests only
	pytest -m integration --cov=src

coverage: ## Show coverage report
	pytest --cov=src --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

lint: ## Run ruff linter
	ruff check src tests

format: ## Format code with black
	black src tests

typecheck: ## Run mypy type checking
	mypy src --ignore-missing-imports

security: ## Security scanning (bandit + safety)
	bandit -r src/ -ll
	safety check --json

docker-up: ## Start docker-compose services
	docker-compose up -d
	@echo "Services started. Health check: curl http://localhost:8000/health"

docker-down: ## Stop docker-compose services
	docker-compose down

docker-logs: ## Tail docker logs
	docker-compose logs -f app

load-test: ## Run K6 load testing
	k6 run load-tests/endpoints.js

load-test-ramp: ## K6 test with custom ramp settings
	k6 run -e BASE_URL=http://localhost:8000 load-tests/endpoints.js

chaos-test: ## Apply chaos engineering experiments
	kubectl apply -f k8s/chaos/network-chaos.yaml
	@echo "Chaos experiments applied. Monitor: kubectl get networkchaos -n default"

helm-install: ## Install helm chart to K8s
	helm install aerosense ./helm --namespace aerosense --create-namespace

helm-upgrade: ## Upgrade helm chart
	helm upgrade aerosense ./helm --namespace aerosense

helm-uninstall: ## Uninstall helm chart
	helm uninstall aerosense --namespace aerosense

metrics: ## Port-forward prometheus
	kubectl port-forward -n aerosense svc/prometheus 9090:9090 &
	@echo "Prometheus available at http://localhost:9090"

dashboard: ## Port-forward grafana
	kubectl port-forward -n aerosense svc/grafana 3000:3000 &
	@echo "Grafana available at http://localhost:3000 (admin/admin)"

clean: ## Clean up build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage
	docker-compose down -v 2>/dev/null || true
