from camagru.lib.response import response
from camagru.lib.template import page


def reset_password() -> tuple[str, list, bytes]:
    return response(
        page("reset-password.html", "Camagru - Reset Password")
    )
