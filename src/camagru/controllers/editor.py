from camagru.lib.request import Request
from camagru.lib.response import redirect, response
from camagru.lib.template import page, render
from camagru.services.image import list_user_images


def editor(request: Request) -> tuple[str, list, bytes]:
    if request.user is None:
        return redirect("/login?required=1")

    images = list_user_images(request.user["id"])
    photos = "".join(
        render("_photo.html", image_id=img["id"], created_at=img["created_at"])
        for img in images
    ) or render("_editor_empty.html")
    return response(
        page(
            "editor.html",
            "Camagru - Edit",
            raw={"photos": photos},
            csrf_token=request.csrf_token,
            user=request.user
        )
    )
