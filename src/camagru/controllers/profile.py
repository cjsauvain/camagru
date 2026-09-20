from camagru.lib.request import Request
from camagru.lib.response import response
from camagru.lib.template import page


def profile(request: Request) -> tuple[str, list, bytes]:
    return response(
        page("profile.html", "Camagru - Profile", nav="_nav_user.html")
    )
