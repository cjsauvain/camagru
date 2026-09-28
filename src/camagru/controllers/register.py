from camagru.lib.request import Request
from camagru.lib.response import redirect, response
from camagru.lib.template import page
from camagru.services.auth import register, confirm_account
from camagru.services.errors import ValidationError


def register_form(request: Request) -> tuple[str, list, bytes]:
    if request.user is not None:
        return redirect("/gallery")

    return response(
        page(
            "register.html",
            "Camagru - Register",
            csrf_token=request.csrf_token,
            user=request.user,
            errors=""
        )
    )


def register_submit(request: Request) -> tuple[str, list, bytes]:
    try:
        register(
            request.form.get("username", ""),
            request.form.get("email", ""),
            request.form.get("password", "")
        )
    
    except ValidationError as e:
        return response(
            page(
                "register.html",
                "Camagru - Register",
                csrf_token=request.csrf_token,
                user=request.user,
                errors=str(e)
            )
        )

    return redirect("/login")


def register_confirm(request: Request, confirm_token: str) -> tuple[str, list, bytes]:
    try:
        confirm_account(confirm_token)
    except ValidationError as e:
        return response(
            page(
                "register.html",
                "Camagru - Register",
                csrf_token=request.csrf_token,
                user=request.user,
                errors=str(e)
            )
        )

    return redirect("/login")