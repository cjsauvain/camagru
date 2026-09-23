from camagru.lib.request import Request
from camagru.lib.response import response
from camagru.lib.template import page
from camagru.services.errors import ValidationError
from camagru.services.auth import request_password_reset


def forgot_password_form(request: Request) -> tuple[str, list, bytes]:
    return response(
        page(
            "forgot-password.html",
            "Camagru - Forgot Password",
            user=request.user,
            errors="",
            message=""
        )
    )


def forgot_password_submit(request: Request) -> tuple[str, list, bytes]:
    try:
        request_password_reset(request.form.get("email", ""))

    except ValidationError as e:
        return response(
            page(
                "forgot-password.html",
                "Camagru - Forgot Password",
                user=request.user,
                errors=str(e),
                message=""
            )
        )

    return response(
        page(
            "forgot-password.html",
            "Camagru - Forgot Password",
            user=request.user,
            errors="",
            message="If this email is registered, a reset link has been sent."
        )
    )
