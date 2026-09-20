from camagru.lib.response import response
from camagru.lib.template import page


def login() -> tuple[str, list, bytes]:
    return response(
        page("login.html", "Camagru - Login")
    )
