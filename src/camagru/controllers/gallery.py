from camagru.lib.response import response
from camagru.lib.template import page


def gallery() -> tuple[str, list, bytes]:
    return response(
        page("gallery.html", "Camagru - Gallery")
    )
