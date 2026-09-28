import re

from camagru.controllers.gallery import gallery
from camagru.controllers.image import (
    editor_image_delete,
    gallery_image_delete,
    image_create,
    image_like,
    image_show,
    comment_create
)
from camagru.controllers.login import login_form, login_submit
from camagru.controllers.logout import logout
from camagru.controllers.register import register_form, register_submit, register_confirm
from camagru.controllers.forgot_password import forgot_password_form, forgot_password_submit
from camagru.controllers.reset_password import reset_password_form, reset_password_submit
from camagru.controllers.profile import (
    profile_form,
    profile_username,
    profile_email,
    profile_password,
    profile_notification
)
from camagru.controllers.editor import editor
from camagru.lib.request import Request
from camagru.lib.response import not_found


def compile_pattern(endpoint: str) -> re.Pattern:
    """
    Translate "/images/<id>/delete" into a compiled regular expression.
    """
    regex = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", endpoint)
    return re.compile(regex)


ROUTES = [
    ("GET", compile_pattern("/"), gallery),
    ("GET", compile_pattern("/gallery"), gallery),
    ("GET", compile_pattern("/login"), login_form),
    ("POST", compile_pattern("/login"), login_submit),
    ("POST", compile_pattern("/logout"), logout),
    ("GET", compile_pattern("/register"), register_form),
    ("GET", compile_pattern("/register/confirm/<confirm_token>"), register_confirm),
    ("POST", compile_pattern("/register"), register_submit),
    ("GET", compile_pattern("/forgot-password"), forgot_password_form),
    ("POST", compile_pattern("/forgot-password"), forgot_password_submit),
    ("GET", compile_pattern("/reset-password/<reset_token>"), reset_password_form),
    ("POST", compile_pattern("/reset-password/<reset_token>"), reset_password_submit),
    ("GET", compile_pattern("/profile"), profile_form),
    ("POST", compile_pattern("/profile/username"), profile_username),
    ("POST", compile_pattern("/profile/email"), profile_email),
    ("POST", compile_pattern("/profile/password"), profile_password),
    ("POST", compile_pattern("/profile/notification"), profile_notification),
    ("GET", compile_pattern("/editor"), editor),
    ("GET", compile_pattern("/images/<image_id>"), image_show),
    ("POST", compile_pattern("/images"), image_create),
    ("POST", compile_pattern("/gallery/<image_id>/delete"), gallery_image_delete),
    ("POST", compile_pattern("/editor/<image_id>/delete"), editor_image_delete),
    ("POST", compile_pattern("/images/<image_id>/likes"), image_like),
    ("POST", compile_pattern("/images/<image_id>/comments"), comment_create),
]


def router(request: Request) -> tuple[str, list, bytes]:
    for method, endpoint, handler in ROUTES:
        match = endpoint.fullmatch(request.path)
        if match and method == request.method:
            return handler(request, **match.groupdict())

    return not_found(request.user)
