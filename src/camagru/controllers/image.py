import re

from camagru.lib.response import forbidden, redirect, response, not_found
from camagru.lib.request import Request
from camagru.services.comment import add_comment
from camagru.services.errors import ValidationError
from camagru.services.image import create_image, delete_image, image_path
from camagru.services.like import toggle_like


def image_create(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return response(
            "You must be logged in.",
            status="401 Unauthorized",
            content_type="text/plain; charset=utf-8"
        )

    overlay_names = [n for n in request.query.get("overlay", "").split(",") if n]
    try:
        image_id = create_image(request.user["id"], request.body, overlay_names)

    except ValidationError as e:
        return response(
            str(e),
            status="400 Bad Request",
            content_type="text/plain; charset=utf-8"
        )

    return response(
        str(image_id),
        status="201 Created",
        content_type="text/plain; charset=utf-8"
    )


def image_show(request: Request, image_id: str) -> tuple[str, list, bytes]:
    if re.fullmatch(r"[0-9]{1,18}", image_id) is None:
        return not_found(request.user)

    path = image_path(int(image_id))
    if path is None or not path.is_file():
        return not_found(request.user)

    return response(path.read_bytes(), content_type="image/png")


def gallery_image_delete(request: Request, image_id: str) -> tuple[str, list, bytes]:
    if request.user is None:
        return response(
            "You must be logged in.",
            status="401 Unauthorized",
            content_type="text/plain; charset=utf-8"
        )

    if re.fullmatch(r"[0-9]{1,18}", image_id) is None:
        return not_found(request.user)

    try:
        delete_image(request.user["id"], int(image_id))

    except ValidationError:
        return forbidden(request.user)

    return redirect("/gallery")


def editor_image_delete(request: Request, image_id: str) -> tuple[str, list, bytes]:
    if request.user is None:
        return response(
            "You must be logged in.",
            status="401 Unauthorized",
            content_type="text/plain; charset=utf-8"
        )

    if re.fullmatch(r"[0-9]{1,18}", image_id) is None:
        return not_found(request.user)

    try:
        delete_image(request.user["id"], int(image_id))

    except ValidationError:
        return forbidden(request.user)

    return redirect("/editor")


def image_like(request: Request, image_id: str) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login?required=1")    

    if re.fullmatch(r"[0-9]{1,18}", image_id) is None:
        return not_found(request.user)

    try:
        toggle_like(request.user["id"], int(image_id))

    except ValidationError:
        return not_found(request.user)

    return redirect("/gallery")


def comment_create(request: Request, image_id: str) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login?required=1")    

    if re.fullmatch(r"[0-9]{1,18}", image_id) is None:
        return not_found(request.user)

    try:
        add_comment(request.user["id"], int(image_id), request.form.get("body", ""))

    except ValidationError:
        return redirect("/gallery?error=comment")

    return redirect("/gallery")
