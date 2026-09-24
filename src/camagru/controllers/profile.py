import sqlite3

from camagru.lib.request import Request
from camagru.lib.response import redirect, response
from camagru.lib.template import page
from camagru.services.errors import ValidationError
from camagru.services.profile import (
    update_email,
    update_notification,
    update_username,
    change_password,
)


def _render_profile(user: sqlite3.Row, errors: str = "") -> tuple[str, list, bytes]:
    return response(
        page(
            "profile.html",
            "Camagru - Profile",
            user=user,
            username=user["username"],
            email=user["email"],
            notification="checked" if user["notify_on_comment"] else "",
            errors=errors,
        )
    )


def profile_form(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login")

    return _render_profile(request.user)


def profile_username(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login")

    try:
        update_username(request.user["id"], request.form.get("username", ""))

    except ValidationError as e:
        return _render_profile(request.user, errors=str(e))

    return redirect("/profile")


def profile_email(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login")

    try:
        update_email(request.user["id"], request.form.get("email", ""))

    except ValidationError as e:
        return _render_profile(request.user, errors=str(e))

    return redirect("/profile")


def profile_password(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login")

    try:
        confirm_password = request.form.get("confirm-password", "")
        new_password = request.form.get("new-password", "")
        if confirm_password != new_password: 
            raise ValidationError("Passwords are not equal.")

        change_password(
            request.user["id"],
            request.form.get("current-password", ""),
            new_password,        )

    except ValidationError as e:
        return _render_profile(request.user, errors=str(e))

    return redirect("/profile")


def profile_notification(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login")

    try:
        update_notification(
            request.user["id"], "notify_on_comment" in request.form
        )

    except ValidationError as e:
        return _render_profile(request.user, errors=str(e))

    return redirect("/profile")
