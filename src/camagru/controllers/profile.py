from camagru.lib.request import Request
from camagru.lib.response import redirect, response
from camagru.lib.template import page


def profile(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login")

    return response(
        page(
            "profile.html",
            "Camagru - Profile",
            user=request.user
        )
    )
