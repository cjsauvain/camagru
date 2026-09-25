CAMAGRU_IMAGE=camagru-app:latest

all: up

up:
	docker compose up -d --build

down:
	docker compose down

rmi:
	docker rmi $(CAMAGRU_IMAGE) -f

rm: down rmi
	docker compose rm -f
	rm -f ./data/camagru.db

re: rm up
