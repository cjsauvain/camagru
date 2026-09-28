# Camagru

Take a picture with your webcam or upload one, pick an overlay, and the
server merges the two. Every result goes to a public gallery where users
can like and comment.

Python standard library only — no framework, no dependencies.

## Run

```sh
cp .env.example .env
docker compose up
```

- Site: <http://localhost:8080>
- Mailpit: <http://localhost:8081>

Account confirmation and password reset emails are delivered to Mailpit.
