from camagru.lib.request import Request
from camagru.lib.response import response
from camagru.lib.template import page


def gallery(request: Request) -> tuple[str, list, bytes]:
    return response(
        page(
            "gallery.html",
            "Camagru - Gallery",
            csrf_token=request.csrf_token,
            user=request.user
        ),
    )
