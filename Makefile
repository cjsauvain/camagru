CAMAGRU_IMAGE=camagru-app:latest

all: up

up:
	docker compose up -d

down:
	docker compose down

rmi:
	docker rmi $(CAMAGRU_IMAGE)

rm: down rmi
	docker compose rm

re: rm up
