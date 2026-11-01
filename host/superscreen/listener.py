"""Hotplug-aware private-interface listeners for USB tethering and hotspots.

The preview is deliberately NOT a Windows Indirect Display Driver (IDD).
It serves an existing monitor over HTTP on explicit RFC1918 interfaces.
"""
from __future__ import annotations

import asyncio
from aiohttp import web

from .network import bind_addresses, discover_lan_ips


class PrivateInterfaceListener:
    """Add/remove local aiohttp sites as USB tethering interfaces appear."""

    def __init__(self, app: web.Application, port: int, *, poll_seconds: float = 4.0):
        if not 1 <= port <= 65535 or poll_seconds <= 0:
            raise ValueError("Invalid listener options")
        self.port = port
        self.poll_seconds = poll_seconds
        self.runner = web.AppRunner(app, handle_signals=False)
        self.sites: dict[str, web.TCPSite] = {}

    async def start(self) -> None:
        await self.runner.setup()
        await self.refresh()

    async def refresh(self) -> None:
        # Discover via hostname + native Windows adapter enumeration.
        wanted = set(bind_addresses(discover_lan_ips()))
        for address in list(self.sites):
            if address not in wanted:
                await self.sites.pop(address).stop()
                print(f"  SuperScreen interface disconnected: {address}", flush=True)
        for address in sorted(wanted - self.sites.keys()):
            try:
                site = web.TCPSite(self.runner, host=address, port=self.port)
                await site.start()
            except OSError as exc:
                # Windows may still be assigning the new tether address.
                print(f"  SuperScreen cannot listen on {address}: {exc}", flush=True)
                continue
            self.sites[address] = site
            print(f"  SuperScreen listening at http://{address}:{self.port}", flush=True)

    async def close(self) -> None:
        await self.runner.cleanup()
        self.sites.clear()

    async def serve_forever(self) -> None:
        try:
            await self.start()
            while True:
                await asyncio.sleep(self.poll_seconds)
                await self.refresh()
        finally:
            await self.close()


async def serve_watched(app: web.Application, port: int) -> None:
    await PrivateInterfaceListener(app, port).serve_forever()
