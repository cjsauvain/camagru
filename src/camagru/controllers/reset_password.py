from camagru.lib.request import Request
from camagru.lib.response import response
from camagru.lib.template import page


def reset_password(request: Request) -> tuple[str, list, bytes]:
    return response(
        page(
            "reset-password.html",
            "Camagru - Reset Password",
            user=request.user,
        )
    )
