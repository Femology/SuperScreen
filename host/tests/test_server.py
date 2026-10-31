from __future__ import annotations

import json

import pytest
from aiohttp import WSMsgType
from aiohttp.test_utils import TestClient, TestServer

from superscreen.auth import PairingManager
from superscreen.server import create_app


@pytest.fixture
def pairing(tmp_path):
    return PairingManager(store_path=tmp_path / "tokens.json")


@pytest.mark.asyncio
async def test_status_and_auth_endpoints(pairing):
    server = TestServer(create_app(pairing))
    async with TestClient(server) as client:
        res = await client.get("/api/status")
        assert res.status == 200
        data = await res.json()
        assert data["mode"] == "mirror"
        assert data["encrypted"] is False
        assert res.headers.get("Cache-Control") == "no-store"
        denied = await client.get("/api/monitors")
        assert denied.status == 401
        denied = await client.post("/api/pair", json={"code": "abcdef"})
        assert denied.status == 401
        res = await client.post("/api/pair", json={"code": pairing.code})
        assert res.status == 200
        token = (await res.json())["token"]
        assert pairing.verify(token)


@pytest.mark.asyncio
async def test_websocket_rejects_invalid_token(pairing):
    server = TestServer(create_app(pairing))
    async with TestClient(server) as client:
        ws = await client.ws_connect("/ws")
        await ws.send_json({"type": "authenticate", "token": "bad"})
        response = await ws.receive(timeout=2)
        assert response.type == WSMsgType.TEXT
        assert json.loads(response.data)["type"] == "error"
        await ws.close()


@pytest.mark.asyncio
async def test_websocket_returns_frame_and_monitor_metadata(pairing, monkeypatch):
    import superscreen.server as mod

    class FakeCapture:
        def __enter__(self): return self
        def __exit__(self, *args): return None
        def frame(self, monitor_index, max_width, quality):
            assert monitor_index in (1, 2)
            return b"\xff\xd8fake-jpeg\xff\xd9"

    monkeypatch.setattr(mod, "CaptureSession", FakeCapture)
    monkeypatch.setattr(mod, "list_monitors", lambda: [
        {"index": 1, "left": 0, "top": 0, "width": 800, "height": 600},
        {"index": 2, "left": 800, "top": 0, "width": 1920, "height": 1080},
    ])
    token = pairing.issue(pairing.code)
    server = TestServer(create_app(pairing, fps=4))
    async with TestClient(server) as client:
        ws = await client.ws_connect("/ws")
        await ws.send_json({"type": "authenticate", "token": token})
        ready = await ws.receive(timeout=3)
        assert json.loads(ready.data)["type"] == "ready"
        await ws.send_json({"type": "select-monitor", "index": 2})
        saw_frame = False
        saw_selected = False
        for _ in range(5):
            msg = await ws.receive(timeout=3)
            if msg.type == WSMsgType.BINARY:
                saw_frame = True
            if msg.type == WSMsgType.TEXT and json.loads(msg.data).get("type") == "selected":
                saw_selected = True
            if saw_frame and saw_selected:
                break
        assert saw_frame and saw_selected
        await ws.close()


def test_reject_invalid_fps(pairing):
    with pytest.raises(ValueError):
        create_app(pairing, fps=0)
