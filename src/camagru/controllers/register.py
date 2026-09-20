from camagru.lib.response import response
from camagru.lib.template import page


def register() -> tuple[str, list, bytes]:
    return response(
        page("register.html", "Camagru - Register")
    )
