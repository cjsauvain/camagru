from camagru.lib.request import Request
from camagru.lib.response import response
from camagru.lib.template import page


def register(request: Request) -> tuple[str, list, bytes]:
    return response(
        page("register.html", "Camagru - Register")
    )
