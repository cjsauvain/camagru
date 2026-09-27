import html
import sqlite3
from string import Template
from pathlib import Path

VIEWS = Path(__file__).parent.parent / "views"


def render(name: str, raw: dict | None = None, **values) -> str:
    template = (VIEWS / name).read_text(encoding="utf-8")
    context = {k: html.escape(str(v)) for k, v in values.items()}
    context.update(raw or {})

    return Template(template).substitute(context)


def page(
    name: str,
    title: str,
    csrf_token: str,
    user: sqlite3.Row | None = None,
    raw: dict | None = None,
    **values,
) -> str:
    content = render(name, raw=raw, csrf_token=csrf_token, **values)
    nav = "_nav_user.html" if user else "_nav_guest.html"
    return render(
        "layout.html",
        raw={"content": content, "nav": render(nav, csrf_token=csrf_token)},
        title=title,
    )
