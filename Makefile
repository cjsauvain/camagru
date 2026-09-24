CAMAGRU_IMAGE=camagru-app:latest

all: up

up:
	docker compose up -d --build

down:
	docker compose down

rmi:
	docker rmi $(CAMAGRU_IMAGE)

rm: down rmi
	docker compose rm
	rm ./data/camagru.db

re: rm up
