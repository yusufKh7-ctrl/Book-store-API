run:
	fastapi dev main.py

format:
	ruff format .

lint:
	ruff check .

fix:
	ruff check --fix .