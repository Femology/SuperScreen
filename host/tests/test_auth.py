from __future__ import annotations

import hashlib
import json

import pytest

from superscreen.auth import PairingManager, PairingRateLimited


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def test_pairing_creates_random_token_and_persists_hash(tmp_path):
    store = tmp_path / "tokens.json"
    clock = Clock()
    manager = PairingManager(store_path=store, clock=clock)
    code = manager.code
    token = manager.issue(code, remote="192.168.43.1")
    assert token is not None
    assert len(token) > 20
    assert manager.verify(token)
    assert not manager.verify("not-a-real-token")
    text = store.read_text()
    assert token not in text
    assert hashlib.sha256(token.encode()).hexdigest() in text
    assert PairingManager(store_path=store, clock=clock).verify(token)
    assert manager.issue(code, remote="192.168.43.1") is None


def test_pairing_code_expires(tmp_path):
    clock = Clock()
    m = PairingManager(store_path=tmp_path / "tokens", clock=clock)
    old = m.code
    clock.advance(301)
    # A code minted 5 minutes ago cannot be accepted.
    # Extremely rare collision probability 1/1e6; patch deterministic code.
    m._new_code = lambda: "222222" if old != "222222" else "333333"
    assert m.issue(old) is None
    assert m.code != old
    assert m.issue(m.code)


def test_attempt_limit_and_window(tmp_path):
    clock = Clock()
    m = PairingManager(store_path=tmp_path / "tokens", clock=clock)
    for _ in range(5):
        assert m.issue("bad", remote="client") is None
    with pytest.raises(PairingRateLimited):
        m.issue(m.code, remote="client")
    # Another address has its own attempt budget.
    assert m.issue(m.code, remote="other")
    clock.advance(61)
    assert m.issue("bad", remote="client") is None


def test_revoke(tmp_path):
    m = PairingManager(store_path=tmp_path / "tokens")
    token = m.issue(m.code)
    assert m.verify(token)
    m.revoke_all()
    assert not m.verify(token)


def test_corrupt_store_ignored(tmp_path):
    path = tmp_path / "tokens"
    path.write_text("not JSON")
    m = PairingManager(store_path=path)
    assert not m.verify("totally bogus")
    path.write_text(json.dumps({"token_sha256": ["wrong", 12]}))
    assert not PairingManager(store_path=path).verify("bogus")
