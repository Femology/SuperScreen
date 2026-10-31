"""Static regression checks for the bundled browser UI.

The browser viewer is shipped inside both the Windows binary and Android launcher.
Check the most failure-prone wiring (element IDs, script syntax, accessibility
basics) without introducing a frontend framework or JavaScript build system.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess

import pytest


HTML = Path(__file__).resolve().parents[1] / "superscreen" / "web" / "index.html"


class ElementInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: list[str] = []
        self.labels: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(attributes["id"])
        if tag == "label" and attributes.get("for"):
            self.labels.append(attributes["for"])


def test_bundled_viewer_has_all_required_app_elements():
    html = HTML.read_text(encoding="utf-8")
    doc = ElementInspector()
    doc.feed(html)
    required = {
        "statusDot", "status", "screen", "screenWrap", "waitingTitle",
        "waitingMessage", "pairPanel", "pairForm", "code", "pairError",
        "monitors", "dimensions", "lastFrame", "fullscreen", "fps",
        "resolution", "forget",
    }
    assert required <= set(doc.ids), sorted(required - set(doc.ids))
    assert len(doc.ids) == len(set(doc.ids)), "Duplicate HTML id"
    assert {"code", "monitors"} <= set(doc.labels)


def test_viewer_has_accessible_mobile_basics_and_no_css_framework():
    html = HTML.read_text(encoding="utf-8").lower()
    assert 'name="viewport"' in html
    assert 'name="theme-color"' in html
    assert "prefers-reduced-motion" in html
    assert 'role="alert"' in html
    assert "aria-live" in html
    assert "shadcn" not in html
    assert "tailwind" not in html


def test_inline_viewer_script_is_valid_javascript():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is optional locally; installed in GitHub Actions")
    html = HTML.read_text(encoding="utf-8")
    match = re.search(r"<script>(.*?)</script>", html, flags=re.DOTALL)
    assert match is not None, "Expected bundled script"
    result = subprocess.run(
        [node, "--check", "--input-type=commonjs", "-"],
        input=match.group(1),
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
