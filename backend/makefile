APP_NAME = src.main
PORT = 8000
HOST = 0.0.0.0
IMAGE_NAME = subtitle-service


dev:
	poetry run python -m uvicorn $(APP_NAME):app --reload --host $(HOST) --port $(PORT)

install: 
	poetry install --no-root

# Docker
build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run -p 8000:8000 \
		-v $(PWD)/data:/app/data \
		-e PORT=8000 \
		$(IMAGE_NAME)
