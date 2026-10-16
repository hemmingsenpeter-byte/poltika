"""Task B0.1.3 (ADR-0023): serve the exported web app from the API process.

`web/` builds to a static export (`web/out`). This middleware serves it so
one image, one origin and one login cover both the UI and the API:

- `/_next/*` and a few top-level static files (favicon and the like) come
  from the export directory. `/_next/static/*` is content-hashed, so it is
  cached immutably.
- A `GET`/`HEAD` whose `Accept` header prefers `text/html` on a declared UI
  route gets the exported page, `no-cache`. Dynamic routes were exported once
  with the placeholder id `_`; the page reads the real id from the URL.
- Client-side navigation fetches a page's RSC payload as `<route>.txt` with
  an `RSC: 1` header (Next's `output: "export"` mode). Such a request on a
  declared UI route gets that page's exported `.txt`, `no-cache`, so a nested
  route (`/scenarios/new.txt`, `/models/<id>.txt`) no longer falls through to
  the API and forces a full reload. Without the header nothing changes.
- Everything else passes through untouched. API clients sending
  `application/json` or `*/*` (so `GET /scenarios/{id}` still returns JSON),
  `/analyst`, `/docs`, `/openapi.json`, `/healthz` and every API route behave
  as before.

The export directory is `POLTIKA_WEB_DIR`, else `<repo>/web/out` when that
exists. With neither, the middleware passes every request through. The
setting is read on each request, like `api/access.py`'s password, so a test
or operator change takes effect at once.

Every cache header is `private`: the responses sit behind the password, so
no shared cache may keep them.

It is registered inside `BasicAuthMiddleware` (`api/main.py`), so pages need
the password like everything else; only `/healthz` is open.
"""

from __future__ import annotations

import mimetypes
import os
import re
from pathlib import Path

from starlette.responses import FileResponse, PlainTextResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

_ID = r"[A-Za-z0-9_.-]{1,128}"
# (path pattern, exported file). Dynamic routes map onto the `_` placeholder.
_UI_ROUTES: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(pattern), page)
    for pattern, page in (
        (r"/", "index.html"),
        (r"/scenarios", "scenarios.html"),
        (r"/scenarios/new", "scenarios/new.html"),
        (rf"/scenarios/{_ID}", "scenarios/_.html"),
        (rf"/scenarios/{_ID}/runs/{_ID}", "scenarios/_/runs/_.html"),
        (r"/models", "models.html"),
        (rf"/models/{_ID}", "models/_.html"),
        (r"/data", "data.html"),
        (rf"/data/{_ID}", "data/_.html"),
        (r"/settings", "settings.html"),
    )
)

# Top-level files a static export may carry. Never `.json`: `/openapi.json`
# belongs to the API, and the export has no JSON a browser needs.
_STATIC_SUFFIXES = frozenset(
    {".ico", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".txt", ".webmanifest", ".xml"}
)
_MEDIA_TYPES = {".woff2": "font/woff2", ".webmanifest": "application/manifest+json"}

_IMMUTABLE = "private, max-age=31536000, immutable"
_REVALIDATE = "private, no-cache"
_SHORT = "private, max-age=3600"


def web_dir() -> Path | None:
    """The export directory, or None when the web app is not installed."""
    configured = os.environ.get("POLTIKA_WEB_DIR")
    candidate = Path(configured) if configured else Path(__file__).resolve().parents[3] / "web" / "out"
    return candidate if candidate.is_dir() else None


def prefers_html(accept: str) -> bool:
    """True when `text/html` is named and outranks `application/json`. `*/*`
    alone never counts, so API clients keep getting the API."""
    quality: dict[str, tuple[float, int]] = {}
    for position, part in enumerate(accept.split(",")):
        fields = [f.strip() for f in part.split(";")]
        media = fields[0].lower()
        q = 1.0
        for field in fields[1:]:
            if field.lower().startswith("q="):
                try:
                    q = float(field[2:])
                except ValueError:
                    q = 0.0
        quality.setdefault(media, (q, position))
    html = quality.get("text/html")
    if html is None or html[0] <= 0:
        return False
    other = quality.get("application/json")
    if other is None or other[0] <= 0:
        return True
    return html[0] > other[0] or (html[0] == other[0] and html[1] < other[1])


def ui_page(path: str) -> str | None:
    """The exported file for a UI route, else None."""
    for pattern, page in _UI_ROUTES:
        if pattern.fullmatch(path):
            return page
    return None


def _safe_file(root: Path, relative: str) -> Path | None:
    """`relative` resolved under `root`, or None for a missing file or any
    attempt to leave it."""
    if "\x00" in relative or "\\" in relative:
        return None
    if any(segment in ("", ".", "..") for segment in relative.split("/")):
        return None
    base = root.resolve()
    try:
        target = (base / relative).resolve()
    except (OSError, ValueError):
        return None
    if not target.is_relative_to(base) or not target.is_file():
        return None
    return target


def _media_type(path: Path) -> str | None:
    return _MEDIA_TYPES.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0]


class WebAppMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] not in ("GET", "HEAD"):
            await self.app(scope, receive, send)
            return
        root = web_dir()
        if root is None:
            await self.app(scope, receive, send)
            return

        path: str = scope["path"]
        if path.startswith("/_next/"):
            file = _safe_file(root, path[1:])
            if file is None:
                await PlainTextResponse("Not Found", status_code=404)(scope, receive, send)
                return
            cache = _IMMUTABLE if path.startswith("/_next/static/") else _SHORT
            await FileResponse(file, media_type=_media_type(file), headers={"cache-control": cache})(
                scope, receive, send
            )
            return

        static = path.count("/") == 1 and Path(path).suffix.lower() in _STATIC_SUFFIXES
        if static:
            file = _safe_file(root, path[1:])
            if file is not None:
                await FileResponse(
                    file, media_type=_media_type(file), headers={"cache-control": _SHORT}
                )(scope, receive, send)
                return

        headers = dict(scope["headers"])
        if path.endswith(".txt") and headers.get(b"rsc") == b"1":
            page = ui_page(path.removesuffix(".txt"))
            file = _safe_file(root, page.removesuffix(".html") + ".txt") if page else None
            if file is not None:
                await FileResponse(
                    file,
                    media_type="text/x-component",
                    headers={"cache-control": _REVALIDATE, "vary": "RSC"},
                )(scope, receive, send)
                return

        page = ui_page(path)
        if page is None:
            await self.app(scope, receive, send)
            return
        accept = headers.get(b"accept", b"").decode("latin-1")
        file = _safe_file(root, page) if prefers_html(accept) else None
        if file is not None:
            await FileResponse(
                file,
                media_type="text/html; charset=utf-8",
                headers={"cache-control": _REVALIDATE, "vary": "Accept"},
            )(scope, receive, send)
            return

        # The same URL answers JSON to API clients: tell caches it varies.
        # A `.txt` path can also be an RSC payload (above), so it varies on that too.
        vary = b"Accept, RSC" if path.endswith(".txt") else b"Accept"

        async def send_varying(message: Message) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = [*message.get("headers", []), (b"vary", vary)]
            await send(message)

        await self.app(scope, receive, send_varying)
