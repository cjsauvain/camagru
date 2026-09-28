import sqlite3

from camagru.lib.request import Request
from camagru.lib.response import redirect, response
from camagru.lib.template import page, render
from camagru.services.image import list_user_images


def _photo(request: Request, img: sqlite3.Row) -> str:
    actions = render(
        "_delete_form.html",
        image_id=img["id"],
        csrf_token=request.csrf_token
    )

    return render(
        "_photo.html",
        raw={"actions": actions},
        image_id=img["id"],
        created_at=img["created_at"]
    )


def editor(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login?required=1")

    images = list_user_images(request.user["id"])
    photos = "".join(_photo(request, img) for img in images) \
        or render("_editor_empty.html")
    return response(
        page(
            "editor.html",
            "Camagru - Edit",
            raw={"photos": photos},
            csrf_token=request.csrf_token,
            user=request.user
        )
    )
