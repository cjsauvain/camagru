
from camagru.lib.request import Request
from camagru.lib.response import redirect, response
from camagru.lib.template import page
from camagru.services.auth import reset_password
from camagru.services.errors import ValidationError


def reset_password_form(request: Request, reset_token: str) -> tuple[str, list, bytes]:
    return response(
        page(
            "reset-password.html",
            "Camagru - Reset Password",
            user=request.user, reset_token=reset_token,
            errors=""
        )
    )


def reset_password_submit(request: Request, reset_token: str) -> tuple[str, list, bytes]:
    try:
        new_password = request.form.get("new-password", "")
        confirm_password = request.form.get("confirm-password", "")

        if new_password != confirm_password:
            raise ValidationError("Passwords are not equal.")

        reset_password(reset_token, new_password)

    except ValidationError as e:
        return response(
            page(
                "reset-password.html",
                "Camagru - Reset Password",
                user=request.user, reset_token=reset_token,
                errors=str(e)
            )
        )

    return redirect("/login")
