from http.cookies import SimpleCookie
import sqlite3
from urllib.parse import parse_qs
from wsgiref.types import WSGIEnvironment

from camagru.lib.security import generate_token

SIZE_MAX = 2_000_000


class Request:
    def __init__(self, environ: WSGIEnvironment) -> None:
        self.method: str = environ["REQUEST_METHOD"]
        self.path: str = environ["PATH_INFO"]
        self.query: dict = self._flatten(
            parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
        )
        self.body: bytes = self._read_body(environ)
        self.form: dict = self._parse_form(environ)
        self.cookies: dict = self._parse_cookies(environ)
        self.csrf_token: str = self.cookies.get("csrf") or generate_token()
        self.x_csrf_token: str = environ.get("HTTP_X_CSRF_TOKEN", "")
        self.user: sqlite3.Row | None = None

    @staticmethod
    def _flatten(d: dict) -> dict:
        return {k: v[0] for k, v in d.items()}

    def _read_body(self, environ: WSGIEnvironment) -> bytes:
        try:
            size = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            size = 0

        if size <= 0 or size > SIZE_MAX:
            return b""

        return environ["wsgi.input"].read(size)

    def _parse_form(self, environ: WSGIEnvironment) -> dict:
        if not environ.get("CONTENT_TYPE", "").startswith(
            "application/x-www-form-urlencoded"
        ):
            return {}

        try:
            decoded_body = self.body.decode('utf-8')
        except UnicodeDecodeError:
            return {}

        return self._flatten(parse_qs(decoded_body, keep_blank_values=True))

    def _parse_cookies(self, environ: WSGIEnvironment) -> dict:
        cookie = SimpleCookie(environ.get("HTTP_COOKIE", ""))
        return {key: morsel.value for key, morsel in cookie.items()}
