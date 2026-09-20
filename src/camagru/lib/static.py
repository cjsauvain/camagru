from pathlib import Path

from camagru.lib.response import from_file, response, not_found


def static(path: str) -> tuple[str, list, bytes]:
    filename = path.removeprefix("/static/")
    static = (Path(__file__).parent.parent / "static").resolve()
    target_file = (static / filename).resolve()

    if not target_file.is_relative_to(static) or not target_file.is_file():
        return not_found()

    body, content_type = from_file(target_file)

    return response(body, content_type=content_type)
