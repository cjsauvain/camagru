import socketserver

from typing import Any
from collections.abc import Iterable
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server
from wsgiref.types import WSGIEnvironment
from camagru.lib.request import Request
from camagru.lib.static import static
from camagru.router import router


class ThreadingWSGIServer(socketserver.ThreadingMixIn, WSGIServer):
    daemon_threads = True


class SilentHandler(WSGIRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass


def app(environ: WSGIEnvironment, start_response) -> Iterable[bytes]:
    request = Request(environ)
    if request.path.startswith("/static/"):
        status, headers, body = static(request.path)
    else:
        status, headers, body = router(request)

    start_response(status, headers)

    return [body]


def serve():
    with make_server(
        "",
        8080,
        app,
        server_class=ThreadingWSGIServer,
        handler_class=SilentHandler
    ) as httpd:
        httpd.serve_forever()
