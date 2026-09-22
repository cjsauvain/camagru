from camagru.lib.request import Request
from camagru.lib.response import response
from camagru.lib.template import page


def forgot_password(request: Request) -> tuple[str, list, bytes]:
    return response(
        page(
            "forgot-password.html",
            "Camagru - Forgot Password",
            user=request.user
        )
    )
