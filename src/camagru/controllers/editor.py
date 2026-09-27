from camagru.lib.request import Request
from camagru.lib.response import redirect, response
from camagru.lib.template import page


def editor(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login")

    return response(
        page(
            "editor.html",
            "Camagru - Edit",
            csrf_token=request.csrf_token,
            user=request.user
        )
    )
