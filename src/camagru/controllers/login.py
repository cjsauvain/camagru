from camagru.lib.request import Request
from camagru.lib.response import redirect, response, set_cookie
from camagru.lib.template import page
from camagru.services.auth import login
from camagru.services.errors import ValidationError


def login_form(request: Request) -> tuple[str, list, bytes]:
    return response(
        page(
            "login.html",
            "Camagru - Login",
            user=request.user,
            errors="",
        )
    )


def login_submit(request: Request) -> tuple[str, list, bytes]:
    try:
        session_id = login(
            request.form.get("username", ""),
            request.form.get("password", "")
        )

    except ValidationError as e:
        return response(
            page(
                "login.html",
                "Camagru - Login",
                user=request.user,
                errors=str(e)
            )
        )

    return redirect("/gallery", [set_cookie("session", session_id, 86400)])
