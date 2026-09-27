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
    content_type: str | None = "text/html; charset=utf-8",
) -> tuple[str, list, bytes]:
    headers = [("Content-Type", content_type or "application/octet-stream")]

    if isinstance(body, str):
        body = body.encode(encoding="utf-8")

    return status, headers, body


def not_found() -> tuple[str, list, bytes]:
    return response(page("404.html", "Camagru - Not Found", ""), status="404 Not Found")


def forbidden() -> tuple[str, list, bytes]:
    return response(page("403.html", "Camagru - Forbidden", ""), status="403 Forbidden")


def redirect(location: str, headers: list | None = None) -> tuple[str, list, bytes]:
    return "302 Found", [("Location", location)] + (headers or []), b""


def server_error() -> tuple[str, list, bytes]:
    return response(
        page("500.html", "Camagru - Internal Server Error", ""),
        status="500 Internal Server Error",
    )


def set_cookie(name: str, value: str, max_age: int) -> tuple[str, str]:
    return (
        "Set-Cookie",
        f"{name}={value}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}",
    )


def clear_cookie(name: str) -> tuple[str, str]:
    return ("Set-Cookie", f"{name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0")