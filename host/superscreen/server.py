"""HTTP pairing + WebSocket screen frames over a trusted local hotspot.

SECURITY: Phase 1 sends unencrypted traffic. See docs/SECURITY.md.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from aiohttp import WSMsgType, web

from .auth import PairingManager, PairingRateLimited
from .capture import CaptureSession, list_monitors


def create_app(
    pairing: PairingManager,
    *,
    monitor: int = 1,
    fps: float = 8,
    max_width: int = 960,
    quality: int = 60,
) -> web.Application:
    if not 1 <= fps <= 15:
        raise ValueError("fps must be between 1 and 15")
    app = web.Application(client_max_size=2048)
    app["pairing"] = pairing
    app["monitor"] = monitor
    app["fps"] = fps
    app["max_width"] = max_width
    app["quality"] = quality
    app["active_viewers"] = 0

    async def security_headers(request: web.Request, response: web.StreamResponse) -> None:
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' blob: data:; "
            "connect-src 'self' ws: wss:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; frame-ancestors 'none'"
        )

    app.on_response_prepare.append(security_headers)

    async def home(request: web.Request) -> web.Response:
        html = Path(__file__).with_name("web").joinpath("index.html").read_text(encoding="utf-8")
        return web.Response(text=html, content_type="text/html")

    async def status(request: web.Request) -> web.Response:
        return web.json_response({
            "name": "SuperScreen",
            "version": "0.1.0",
            "mode": "mirror",
            "paired": False,  # Never reveal whether individual phones are paired.
            "encrypted": False,
            "receiver": "browser",
        })

    async def pair(request: web.Request) -> web.Response:
        try:
            body = await request.json()
        except (ValueError, json.JSONDecodeError):
            raise web.HTTPBadRequest(text="Expected JSON")
        if not isinstance(body, dict):
            raise web.HTTPBadRequest(text="Expected JSON object")
        try:
            token = pairing.issue(body.get("code"), request.remote or "unknown")
        except PairingRateLimited:
            raise web.HTTPTooManyRequests(text="Too many attempts; retry in one minute")
        if token is None:
            raise web.HTTPUnauthorized(text="Incorrect or expired pairing code")
        # Display the newly generated next code only in the trusted host terminal.
        print(f"New one-time pairing code: {pairing.code}", flush=True)
        return web.json_response({"token": token})

    async def monitors(request: web.Request) -> web.Response:
        authorization = request.headers.get("Authorization", "")
        token = authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else ""
        if not pairing.verify(token):
            raise web.HTTPUnauthorized(text="Pairing required")
        try:
            available = list_monitors()
        except Exception as exc:
            raise web.HTTPServiceUnavailable(text=f"Capture unavailable: {type(exc).__name__}")
        return web.json_response({"monitors": available, "default_monitor": app["monitor"]})

    async def stream(request: web.Request) -> web.StreamResponse:
        if app["active_viewers"] >= 2:
            raise web.HTTPTooManyRequests(text="Maximum two viewers in this prototype")
        # Prevent a web page at another origin from initiating authenticated control.
        origin = request.headers.get("Origin")
        expected = f"{request.scheme}://{request.host}"
        if origin and origin != expected:
            raise web.HTTPForbidden(text="Unexpected origin")

        ws = web.WebSocketResponse(heartbeat=30, max_msg_size=4096, compress=False)
        await ws.prepare(request)
        app["active_viewers"] += 1
        task: asyncio.Task[None] | None = None
        try:
            try:
                msg = await asyncio.wait_for(ws.receive(), timeout=8)
                packet = json.loads(msg.data) if msg.type == WSMsgType.TEXT else {}
            except (asyncio.TimeoutError, ValueError, TypeError):
                packet = {}
            if (
                not isinstance(packet, dict)
                or packet.get("type") != "authenticate"
                or not pairing.verify(packet.get("token"))
            ):
                await ws.send_json({"type": "error", "message": "Pairing required"})
                await ws.close(code=1008)
                return ws

            selected = {"index": app["monitor"]}
            available = list_monitors()
            allowed = {m["index"] for m in available}
            if selected["index"] not in allowed and allowed:
                selected["index"] = min(allowed)
            await ws.send_json({
                "type": "ready",
                "monitors": available,
                "selected": selected["index"],
                "fps": app["fps"],
            })

            async def send_frames() -> None:
                interval = 1 / app["fps"]
                try:
                    with CaptureSession() as capture:
                        while not ws.closed:
                            start = asyncio.get_running_loop().time()
                            payload = capture.frame(selected["index"], app["max_width"], app["quality"])
                            await ws.send_bytes(payload)
                            elapsed = asyncio.get_running_loop().time() - start
                            await asyncio.sleep(max(0.001, interval - elapsed))
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    if not ws.closed:
                        await ws.send_json({
                            "type": "error",
                            "message": f"Screen capture failed ({type(exc).__name__})."
                        })
                        await ws.close()

            task = asyncio.create_task(send_frames())
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        message = json.loads(msg.data)
                    except ValueError:
                        continue
                    if isinstance(message, dict) and message.get("type") == "select-monitor":
                        candidate = message.get("index")
                        if type(candidate) is int and candidate in allowed:
                            selected["index"] = candidate
                            await ws.send_json({"type": "selected", "index": candidate})
                elif msg.type in (WSMsgType.ERROR, WSMsgType.CLOSE, WSMsgType.CLOSED):
                    break
        finally:
            if task is not None:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
            app["active_viewers"] -= 1
        return ws

    app.router.add_get("/", home)
    app.router.add_get("/api/status", status)
    app.router.add_post("/api/pair", pair)
    app.router.add_get("/api/monitors", monitors)
    app.router.add_get("/ws", stream)
    return app
