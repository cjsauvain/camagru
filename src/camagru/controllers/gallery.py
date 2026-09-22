from camagru.lib.request import Request
from camagru.lib.response import response
from camagru.lib.template import page


def gallery(request: Request) -> tuple[str, list, bytes]:
    return response(
        page(
            "gallery.html",
            "Camagru - Gallery",
            user=request.user
        ),
    )
