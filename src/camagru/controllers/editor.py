from camagru.lib.request import Request
from camagru.lib.response import response
from camagru.lib.template import page


def editor(request: Request) -> tuple[str, list, bytes]:
    return response(
        page("editor.html", "Camagru - Take a photo", nav="_nav_user.html")
    )
