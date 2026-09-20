from camagru.lib.response import response
from camagru.lib.template import page


def forgot_password() -> tuple[str, list, bytes]:
    return response(
        page("forgot-password.html", "Camagru - Forgot Password")
    )
