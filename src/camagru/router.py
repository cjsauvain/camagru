import re

from camagru.controllers.gallery import gallery
from camagru.controllers.login import login
from camagru.controllers.register import register
from camagru.controllers.forgot_password import forgot_password
from camagru.controllers.reset_password import reset_password
from camagru.controllers.profile import profile
from camagru.controllers.editor import editor
from camagru.lib.request import Request
from camagru.lib.response import not_found


def compile_pattern(endpoint: str) -> re.Pattern:
    """
    Translate "/images/<id>/delete" into a compiled regular expression.
    """
    regex = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", endpoint)
    return re.compile(regex)


ROUTES = [
    ("GET", compile_pattern("/"), gallery),
    ("GET", compile_pattern("/gallery"), gallery),
    ("GET", compile_pattern("/login"), login),
    ("GET", compile_pattern("/register"), register),
    ("GET", compile_pattern("/forgot-password"), forgot_password),
    ("GET", compile_pattern("/reset-password"), reset_password),
    ("GET", compile_pattern("/profile"), profile),
    ("GET", compile_pattern("/editor"), editor),
]


def router(request: Request) -> tuple[str, list, bytes]:
    for method, endpoint, handler in ROUTES:
        match = endpoint.fullmatch(request.path)
        if match and method == request.method:
            return handler(request, **match.groupdict())

    return not_found()
