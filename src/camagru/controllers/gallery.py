
import sqlite3

from camagru.lib.request import Request
from camagru.lib.response import not_found, response
from camagru.lib.template import page, render
from camagru.services.errors import ValidationError
from camagru.services.image import list_gallery


def _card(request: Request, img: sqlite3.Row) -> str:
    parts = []
    if request.user:
        parts.append(
            render(
                "_like_form.html",
                image_id=img["id"],
                csrf_token=request.csrf_token
            )
        )
        if img["user_id"] == request.user["id"]:
            parts.append(
                render(
                    "_delete_form.html",
                    image_id=img["id"],
                    csrf_token=request.csrf_token
                )
            )

    actions = "".join(parts)    

    return render(
        "_gallery_image.html",
        raw={"actions": actions},
        image_id=img["id"],
        username=img["username"],
        created_at=img["created_at"],
        likes_count=img["likes_count"]
    )


def gallery(request: Request) -> tuple[str, list, bytes]:
    raw_page = request.query.get("page", "1")
    page_index = int(raw_page) if raw_page.isdigit() else 1

    try:
        page_images, page_count = list_gallery(page_index)
        cards = "".join(_card(request, img) for img in page_images) \
            or render("_gallery_empty.html")
        prev_link = render("_page_link.html", page=page_index - 1, label="Previous") if page_index > 1 else ""
        next_link = render("_page_link.html", page=page_index + 1, label="Next") if page_index < page_count else ""
        raw_content = {"image": cards, "prev": prev_link, "next": next_link}
    
    except ValidationError:
        return not_found()

    return response(
        page(
            "gallery.html",
            "Camagru - Gallery",
            raw=raw_content,
            csrf_token=request.csrf_token,
            user=request.user
        ),
    )
