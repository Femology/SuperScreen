"""Pairing codes and durable *hashed* viewer tokens.

This is a trusted-hotspot prototype, NOT a production secure pairing protocol:
HTTP/WebSocket traffic is unencrypted. See docs/SECURITY.md.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import time
from typing import Callable


class PairingRateLimited(Exception):
    """Too many unsuccessful pairing attempts from the same address."""


def default_store_path() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    root = Path(base) if base else Path.home() / ".superscreen"
    return root / "SuperScreen" / "paired-devices.json" if base else root / "paired-devices.json"


class PairingManager:
    def __init__(
        self,
        store_path: Path | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.store_path = Path(store_path) if store_path is not None else default_store_path()
        self.clock = clock
        self._hashes: set[str] = set()
        self._failed: dict[str, list[float]] = {}
        self._code = self._new_code()
        self._expires = self.clock() + 300
        self._load()

    @staticmethod
    def _new_code() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def _digest(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _load(self) -> None:
        try:
            document = json.loads(self.store_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        tokens = document.get("token_sha256", []) if isinstance(document, dict) else []
        if isinstance(tokens, list):
            self._hashes = {
                item for item in tokens
                if isinstance(item, str) and re.fullmatch(r"[0-9a-f]{64}", item)
            }

    def _save(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        pending = self.store_path.with_suffix(".tmp")
        pending.write_text(
            json.dumps({"token_sha256": sorted(self._hashes)}, indent=2),
            encoding="utf-8",
        )
        os.replace(pending, self.store_path)

    @property
    def code(self) -> str:
        if self.clock() >= self._expires:
            self.rotate_code()
        return self._code

    def rotate_code(self) -> None:
        self._code = self._new_code()
        self._expires = self.clock() + 300

    def issue(self, code: str, remote: str = "unknown") -> str | None:
        now = self.clock()
        attempts = [t for t in self._failed.get(remote, []) if now - t < 60]
        self._failed[remote] = attempts
        if len(attempts) >= 5:
            raise PairingRateLimited("Too many failed attempts; retry in a minute")
        if not isinstance(code, str) or not re.fullmatch(r"[0-9]{6}", code) or not secrets.compare_digest(code, self.code):
            attempts.append(now)
            return None
        self._failed.pop(remote, None)
        token = secrets.token_urlsafe(32)
        self._hashes.add(self._digest(token))
        self._save()
        self.rotate_code()  # Single-use pairing code
        return token

    def verify(self, token: str | None) -> bool:
        return (
            isinstance(token, str)
            and 20 <= len(token) <= 256
            and self._digest(token) in self._hashes
        )

    def revoke_all(self) -> None:
        self._hashes.clear()
        self._save()
