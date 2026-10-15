"""Task B0.1.3 (ADR-0023): the web app is served from the API process
(`api/web.py`) without changing any API behaviour."""

from __future__ import annotations

import asyncio
import base64
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from starlette.types import Message, Scope

from poltika.api.main import app
from poltika.api.web import WebAppMiddleware, prefers_html

HTML = {"Accept": "text/html"}
JSON = {"Accept": "application/json"}
ZEROS = "0" * 64
GATED_TERMS = (
    "digital twin",
    "decision intelligence",
    "decision infrastructure",
    "scientific layer",
    "policy search",
    "predictive",
    "forecast",
)


@pytest.fixture
def web_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A tiny export: each page says which file it is."""
    root = tmp_path / "out"
    for name in (
        "index.html",
        "models.html",
        "data.html",
        "scenarios.html",
        "scenarios/new.html",
        "scenarios/_.html",
        "models/_.html",
        "data/_.html",
        "scenarios/_/runs/_.html",
    ):
        page = root / name
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(f"<!doctype html><title>{name}</title>")
        # The export's RSC payload beside each page (`output: "export"`).
        page.with_suffix(".txt").write_text(f"0:rsc {name}")
    (root / "_next" / "static").mkdir(parents=True)
    (root / "_next" / "static" / "x.js").write_text("console.log(1)")
    (root / "favicon.ico").write_bytes(b"\x00\x00\x01\x00")
    (root / "secret.json").write_text("{}")
    (tmp_path / "outside.txt").write_text("outside the export")
    monkeypatch.setenv("POLTIKA_WEB_DIR", str(root))
    monkeypatch.delenv("POLTIKA_ACCESS_PASSWORD", raising=False)
    monkeypatch.delenv("POLTIKA_REQUIRE_ACCESS_PASSWORD", raising=False)
    monkeypatch.delenv("POLTIKA_DATABASE_URL", raising=False)
    return root


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    ("path", "page"),
    [
        ("/", "index.html"),
        ("/models", "models.html"),
        ("/models/wff_engine", "models/_.html"),
        ("/data", "data.html"),
        ("/data/stats_nz_household_net_worth", "data/_.html"),
        ("/scenarios", "scenarios.html"),
        ("/scenarios/new", "scenarios/new.html"),
        (f"/scenarios/{ZEROS}", "scenarios/_.html"),
        (f"/scenarios/{ZEROS}/runs/{'f' * 64}", "scenarios/_/runs/_.html"),
    ],
)
def test_ui_routes_serve_their_exported_page(
    client: TestClient, web_dir: Path, path: str, page: str
) -> None:
    response = client.get(path, headers=HTML)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.headers["cache-control"] == "private, no-cache"
    assert f"<title>{page}</title>" in response.text
    assert "content-security-policy" in response.headers  # still inside the headers layer


def test_a_browser_accept_header_gets_the_page(client: TestClient, web_dir: Path) -> None:
    browser = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8"
    response = client.get("/models", headers={"Accept": browser})
    assert "<title>models.html</title>" in response.text


def test_head_is_served_without_a_body(client: TestClient, web_dir: Path) -> None:
    response = client.head("/models", headers=HTML)
    assert response.status_code == 200
    assert response.content == b""


def test_next_static_is_immutable(client: TestClient, web_dir: Path) -> None:
    response = client.get("/_next/static/x.js")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "private, max-age=31536000, immutable"
    assert response.text == "console.log(1)"


def test_a_top_level_static_file_is_served(client: TestClient, web_dir: Path) -> None:
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.content == b"\x00\x00\x01\x00"


def test_a_missing_next_file_is_404(client: TestClient, web_dir: Path) -> None:
    assert client.get("/_next/static/nope.js").status_code == 404


def test_top_level_json_in_the_export_is_not_served(client: TestClient, web_dir: Path) -> None:
    assert client.get("/secret.json").status_code == 404


@pytest.mark.parametrize(
    "path",
    [
        "/_next/../../outside.txt",
        "/_next/static/../../../outside.txt",
        "/_next/%2e%2e/%2e%2e/outside.txt",
        "/_next//etc/passwd",
        "/_next/static/..\\..\\outside.txt",
    ],
)
def test_traversal_is_refused(web_dir: Path, path: str) -> None:
    """Sent as raw ASGI paths, so no client normalises them first."""
    sent: list[Message] = []
    reached_app = False

    async def inner(scope: Scope, receive: Any, send: Any) -> None:
        nonlocal reached_app
        reached_app = True

    async def receive() -> Message:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: Message) -> None:
        sent.append(message)

    decoded = path.replace("%2e", ".")
    scope: Scope = {
        "type": "http",
        "method": "GET",
        "path": decoded,
        "headers": [],
    }
    asyncio.run(WebAppMiddleware(inner)(scope, receive, send))
    start = next(m for m in sent if m["type"] == "http.response.start")
    body = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
    assert start["status"] == 404
    assert b"outside the export" not in body
    assert not reached_app


def test_traversal_over_http_never_leaks(client: TestClient, web_dir: Path) -> None:
    response = client.get("/_next/../../etc/passwd")
    assert response.status_code in (401, 404)
    assert "root:" not in response.text


RSC = {"RSC": "1", "Accept": "*/*"}


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/scenarios/new.txt", "scenarios/new.html"),
        (f"/scenarios/{ZEROS}.txt", "scenarios/_.html"),
        (f"/scenarios/{ZEROS}/runs/{'f' * 64}.txt", "scenarios/_/runs/_.html"),
        ("/models/wff_engine.txt", "models/_.html"),
        ("/data/stats_nz_household_net_worth.txt", "data/_.html"),
    ],
)
def test_client_navigation_gets_the_nested_rsc_payload(
    client: TestClient, web_dir: Path, path: str, payload: str
) -> None:
    # Before the fix these fell through to the API (422, 404) and Next
    # reloaded the whole page on every navigation.
    response = client.get(f"{path}?_rsc=abc12", headers=RSC)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/x-component")
    assert response.headers["cache-control"] == "private, no-cache"
    assert response.text == f"0:rsc {payload}"


def test_top_level_rsc_payloads_are_still_static_files(client: TestClient, web_dir: Path) -> None:
    for path, payload in (("/index.txt", "index.html"), ("/scenarios.txt", "scenarios.html")):
        response = client.get(f"{path}?_rsc=abc12", headers=RSC)
        assert response.status_code == 200
        assert response.text == f"0:rsc {payload}"


def test_a_txt_path_without_the_rsc_header_is_unchanged(client: TestClient, web_dir: Path) -> None:
    # `.` is a legal id character, so this is still the scenario API route.
    response = client.get(f"/scenarios/{ZEROS}.txt", headers=JSON)
    assert response.headers["content-type"].startswith("application/json")
    assert "0:rsc" not in response.text
    assert "0:rsc" not in client.get("/models/wff_engine.txt", headers={"RSC": "0"}).text


def test_rsc_on_an_unlisted_path_is_not_a_payload(client: TestClient, web_dir: Path) -> None:
    for path in ("/nowhere.txt", "/models/a/b.txt", "/scenarios/new/x.txt"):
        response = client.get(path, headers=RSC)
        assert response.status_code == 404
        assert "0:rsc" not in response.text


def test_json_clients_still_reach_the_api(client: TestClient, web_dir: Path) -> None:
    for headers in (JSON, {"Accept": "*/*"}, {}):
        response = client.get(f"/scenarios/{ZEROS}", headers=headers)
        assert response.status_code == 503  # no database: the JSON route answered
        assert response.headers["content-type"].startswith("application/json")
        assert response.headers["vary"] == "Accept"


def test_json_wins_when_listed_first(client: TestClient, web_dir: Path) -> None:
    response = client.get(f"/scenarios/{ZEROS}", headers={"Accept": "application/json, text/html"})
    assert response.headers["content-type"].startswith("application/json")


def test_existing_routes_are_unchanged(client: TestClient, web_dir: Path) -> None:
    analyst = client.get("/analyst", headers=HTML)
    assert analyst.status_code == 200
    assert "Poltika analyst" in analyst.text
    assert client.get("/analyst/microsim", headers=HTML).status_code == 200
    assert client.get("/docs", headers=HTML).status_code == 200
    assert client.get("/openapi.json").json()["info"]["title"] == "Poltika API"
    assert client.get("/healthz", headers=HTML).json() == {"status": "ok"}
    assert client.get("/api/v1/meta", headers=HTML).json()["service"] == "poltika"


def test_other_methods_pass_through(client: TestClient, web_dir: Path) -> None:
    response = client.post("/models", headers=HTML)
    assert response.status_code == 404  # the API has no such route; no page was served
    assert "<title>" not in response.text


def test_an_unlisted_path_is_not_a_page(client: TestClient, web_dir: Path) -> None:
    assert client.get("/nowhere", headers=HTML).status_code == 404
    assert client.get("/models/a/b", headers=HTML).status_code == 404
    assert client.get(f"/models/{'a' * 129}", headers=HTML).status_code == 404


def test_pages_need_the_password_but_healthz_does_not(
    client: TestClient, web_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("POLTIKA_ACCESS_PASSWORD", "s3cret")
    assert client.get("/", headers=HTML).status_code == 401
    assert client.get("/models/wff_engine", headers=HTML).status_code == 401
    assert client.get("/_next/static/x.js").status_code == 401
    assert client.get("/models/wff_engine.txt", headers=RSC).status_code == 401
    assert client.get("/healthz").status_code == 200
    token = base64.b64encode(b"pilot:s3cret").decode()
    ok = client.get("/", headers={**HTML, "Authorization": f"Basic {token}"})
    assert ok.status_code == 200
    assert "<title>index.html</title>" in ok.text


def test_everything_passes_through_without_a_web_dir(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("POLTIKA_WEB_DIR", str(tmp_path / "does-not-exist"))
    monkeypatch.delenv("POLTIKA_ACCESS_PASSWORD", raising=False)
    assert client.get("/", headers=HTML).status_code == 404
    assert client.get("/models", headers=HTML).status_code == 404
    assert client.get("/_next/static/x.js").status_code == 404
    assert client.get("/analyst", headers=HTML).status_code == 200


@pytest.mark.parametrize(
    ("accept", "expected"),
    [
        ("text/html", True),
        ("text/html,application/xhtml+xml,*/*;q=0.8", True),
        ("application/json", False),
        ("*/*", False),
        ("", False),
        ("text/html;q=0", False),
        ("text/html;q=0.5, application/json", False),
        ("application/json, text/html", False),
        ("text/html, application/json", True),
        ("text/html;q=0.9, application/json;q=0.8", True),
        ("text/html;q=oops", False),
    ],
)
def test_prefers_html(accept: str, expected: bool) -> None:
    assert prefers_html(accept) is expected


def test_the_built_export_carries_no_gated_term() -> None:
    """If `web/out` has been built, scan every HTML page in it (ADR-0023)."""
    out = Path(__file__).resolve().parents[3] / "web" / "out"
    if not out.is_dir():
        pytest.skip("web/out is not built")
    pages = sorted(out.rglob("*.html"))
    assert pages, "web/out exists but holds no pages"
    for page in pages:
        text = page.read_text(encoding="utf-8").lower()
        found = [term for term in GATED_TERMS if term in text]
        assert not found, f"{page.relative_to(out)} contains {found}"
