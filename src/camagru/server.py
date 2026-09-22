import socketserver

import traceback
from typing import Any
from collections.abc import Iterable
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server
from wsgiref.types import WSGIEnvironment
from camagru.lib.request import Request
from camagru.lib.response import server_error
from camagru.lib.static import static
from camagru.router import router
from camagru.services.auth import current_user


class ThreadingWSGIServer(socketserver.ThreadingMixIn, WSGIServer):
    daemon_threads = True


class SilentHandler(WSGIRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass


def app(environ: WSGIEnvironment, start_response) -> Iterable[bytes]:
    try:
        request = Request(environ)
        if request.path.startswith("/static/"):
            status, headers, body = static(request.path)
        else:
            request.user = current_user(request.cookies.get("session"))
            status, headers, body = router(request)

    except Exception:
        traceback.print_exc(file=environ["wsgi.errors"])
        status, headers, body = server_error()

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
