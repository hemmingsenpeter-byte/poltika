"""Password protection for a hosted pilot (HTTP Basic authentication).

Operator configuration, like the policy directory and the population
(ADR-0011):

- `POLTIKA_ACCESS_PASSWORD`: when set, every route except `/healthz` needs
  it. The username is `POLTIKA_ACCESS_USER` (default `pilot`).
- `POLTIKA_REQUIRE_ACCESS_PASSWORD=1`: the app refuses to start without a
  password. The pilot image sets it, so a hosted container can't come up
  open by mistake. A source checkout doesn't, so local development is
  unchanged.
- `RENDER` (set by Render on every service): treated like
  `POLTIKA_REQUIRE_ACCESS_PASSWORD=1`, so a Render service refuses to start
  without a password even when it isn't built from the pilot image.

Credentials are compared in constant time and never logged. Basic
authentication sends them with every request, so a hosted pilot must be
served over HTTPS (every platform in `docs/pilot/HOSTING.md` does).
"""

from __future__ import annotations

import base64
import binascii
import os
import secrets

from starlette.types import ASGIApp, Receive, Scope, Send

OPEN_PATHS = frozenset({"/healthz"})  # platform health checks; says nothing about the service
_REALM = 'Basic realm="Poltika pilot", charset="UTF-8"'


class AccessConfigError(RuntimeError):
    pass


def configured_credentials() -> tuple[str, str] | None:
    """The (user, password) the operator set, or None when access is open.
    Refuses an open app when `POLTIKA_REQUIRE_ACCESS_PASSWORD` is set or
    the app is running on Render."""
    password = os.environ.get("POLTIKA_ACCESS_PASSWORD", "")
    if not password:
        if os.environ.get("POLTIKA_REQUIRE_ACCESS_PASSWORD") == "1" or os.environ.get("RENDER"):
            raise AccessConfigError(
                "a password is required here (POLTIKA_REQUIRE_ACCESS_PASSWORD or RENDER is set) "
                "but POLTIKA_ACCESS_PASSWORD is empty: set a password (docs/pilot/HOSTING.md)"
            )
        return None
    return os.environ.get("POLTIKA_ACCESS_USER") or "pilot", password


def _authorised(header: bytes | None, user: str, password: str) -> bool:
    if header is None or not header.startswith(b"Basic "):
        return False
    try:
        decoded = base64.b64decode(header[6:].strip(), validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return False
    given_user, sep, given_password = decoded.partition(":")
    if not sep:
        return False
    # Both comparisons always run, so timing doesn't reveal which one failed.
    user_ok = secrets.compare_digest(given_user.encode(), user.encode())
    password_ok = secrets.compare_digest(given_password.encode(), password.encode())
    return user_ok and password_ok


class BasicAuthMiddleware:
    """Checks credentials on every HTTP request, read from the environment
    on each request so a test or operator change takes effect at once."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in OPEN_PATHS:
            await self.app(scope, receive, send)
            return
        credentials = configured_credentials()
        if credentials is None:
            await self.app(scope, receive, send)
            return
        header = dict(scope["headers"]).get(b"authorization")
        if _authorised(header, *credentials):
            await self.app(scope, receive, send)
            return
        await send(
            {
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"www-authenticate", _REALM.encode()),
                    (b"content-type", b"application/json"),
                    (b"cache-control", b"no-store"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": b'{"detail":"authentication required"}'})
