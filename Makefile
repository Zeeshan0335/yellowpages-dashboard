.PHONY: install lint fmt test run up down monitor
install:
	pip install -r requirements-dev.txt
lint:
	ruff check .
fmt:
	ruff check --fix .
test:
	MONGODB_URI=mongodb://localhost:27017/test pytest -q --cov=. --cov-report=term-missing
run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000
up:
	docker compose up -d
down:
	docker compose down
monitor:
	docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
