import mimetypes
from pathlib import Path

from camagru.lib.template import page


def from_file(target_file: Path) -> tuple[bytes, str | None]:
    body = target_file.read_bytes()
    mime_type, _ = mimetypes.guess_type(target_file.name)

    return body, mime_type


def response(
    body: str | bytes,
    status: str = "200 OK",
    content_type: str | None = "text/html; charset=utf-8"
) -> tuple[str, list, bytes]:
    headers = [("Content-Type", content_type or "application/octet-stream")]

    if isinstance(body, str):
        body = body.encode(encoding='utf-8')

    return status, headers, body


def not_found() -> tuple[str, list, bytes]:
    return response(
        page("404.html", "Camagru - Not Found"),
        status="404 Not Found"
    )
