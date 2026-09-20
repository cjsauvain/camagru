from http.cookies import SimpleCookie
from urllib.parse import parse_qs
from wsgiref.types import WSGIEnvironment

SIZE_MAX = 2_000_000


class Request:
    def __init__(self, environ: WSGIEnvironment) -> None:
        self.method = environ["REQUEST_METHOD"]
        self.path = environ["PATH_INFO"]
        self.query = self._flatten(
            parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
        )
        self.form = self._parse_form(environ)
        self.cookies = self._parse_cookies(environ)

    @staticmethod
    def _flatten(d: dict) -> dict:
        return {k: v[0] for k, v in d.items()}

    def _parse_form(self, environ: WSGIEnvironment) -> dict:
        size = int(environ.get("CONTENT_LENGTH") or 0)

        if size == 0 or size > SIZE_MAX:
            return {}

        if not environ.get("CONTENT_TYPE", "").startswith(
            "application/x-www-form-urlencoded"
        ):
            return {}

        text = environ["wsgi.input"].read(size).decode('utf-8')
        return self._flatten(parse_qs(text, keep_blank_values=True))

    def _parse_cookies(self, environ: WSGIEnvironment) -> dict:
        cookie = SimpleCookie(environ.get("HTTP_COOKIE", ""))
        return {key: morsel.value for key, morsel in cookie.items()}
