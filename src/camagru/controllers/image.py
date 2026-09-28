import re

from camagru.lib.response import forbidden, redirect, response, not_found
from camagru.lib.request import Request
from camagru.services.errors import ValidationError
from camagru.services.image import create_image, delete_image, image_path


def image_create(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return response(
            "You must be logged in.",
            status="401 Unauthorized",
            content_type="text/plain; charset=utf-8"
        )

    overlay_name = request.query.get("overlay", "")
    try:
        image_id = create_image(request.user["id"], request.body, overlay_name)

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
        return not_found()

    path = image_path(int(image_id))
    if path is None or not path.is_file():
        return not_found()

    return response(path.read_bytes(), content_type="image/png")


def image_delete(request: Request, image_id: str) -> tuple[str, list, bytes]:
    if request.user is None:
        return response(
            "You must be logged in.",
            status="401 Unauthorized",
            content_type="text/plain; charset=utf-8"
        )

    if re.fullmatch(r"[0-9]{1,18}", image_id) is None:
        return not_found()

    try:
        delete_image(request.user["id"], int(image_id))

    except ValidationError:
        return forbidden()

    return redirect("/gallery")