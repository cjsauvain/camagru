import html
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
    nav: str = "_nav_guest.html",
    raw: dict | None = None,
    **values,
):
    content = render(name, raw=raw, **values)
    return render(
        "layout.html",
        raw={"content": content, "nav": render(nav)},
        title=title
    )
