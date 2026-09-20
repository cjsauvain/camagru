from camagru.controllers.gallery import gallery
from camagru.controllers.login import login
from camagru.controllers.register import register
from camagru.controllers.forgot_password import forgot_password
from camagru.controllers.reset_password import reset_password
from camagru.controllers.profile import profile
from camagru.controllers.editor import editor
from camagru.lib.response import not_found

ROUTES = [
    ("GET", "/", gallery),
    ("GET", "/gallery", gallery),
    ("GET", "/login", login),
    ("GET", "/register", register),
    ("GET", "/forgot-password", forgot_password),
    ("GET", "/reset-password", reset_password),
    ("GET", "/profile", profile),
    ("GET", "/editor", editor),
]


def router(path: str, method: str) -> tuple[str, list, bytes]:
    for route_method, route_endpoint, handler in ROUTES:
        if path == route_endpoint and method == route_method:
            return handler()

    return not_found()
