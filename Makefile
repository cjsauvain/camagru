all: up

up:
	docker compose up -d --build

down:
	docker compose down

fclean:
	docker compose down -v

re: fclean up

.PHONY: all up down fclean re