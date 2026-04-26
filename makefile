APP_NAME = src.main
PORT = 8000
HOST = 0.0.0.0

dev:
	poetry run uvicorn $(APP_NAME):app --reload --host $(HOST) --port $(PORT)