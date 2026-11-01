"""Launch the SuperScreen experimental Windows desktop-mirroring host.

This is NOT an IDD virtual-monitor driver. Use only a trusted local USB
tether or password-protected personal hotspot while transport is unencrypted.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

from .auth import PairingManager
from .capture import list_monitors
from .listener import serve_watched
from .network import discover_lan_ips, bind_addresses
from .server import create_app


def main() -> None:
    p = argparse.ArgumentParser(description="SuperScreen private-network mirroring prototype")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--monitor", type=int, default=1, help="Existing Windows monitor index")
    p.add_argument("--fps", type=float, default=8, help="1-15; keep low on older laptops")
    p.add_argument("--max-width", type=int, default=960, help="JPEG frame width 160-3840")
    p.add_argument("--quality", type=int, default=60, help="JPEG quality 20-95")
    args = p.parse_args()

    if sys.platform.startswith("linux"):
        session = os.environ.get("XDG_SESSION_TYPE", "unknown")
        print(f"  Linux test session: {session}")
        if session.lower() != "x11":
            print("  WARNING: screenshot capture uses MSS/X11; Wayland may be unavailable.")
        print("  Linux mirroring experiment only: no Linux/Windows virtual display driver.")
    elif sys.platform != "win32":
        print("Warning: this operating system has not been validated.")
    if not (1 <= args.port <= 65535 and 160 <= args.max_width <= 3840 and 20 <= args.quality <= 95):
        p.error("Invalid port, width or quality")

    pairing = PairingManager()
    print("\n  SuperScreen 0.1 — experimental Windows mirror to Android")
    print("  WARNING: unencrypted local traffic. Use only private USB or hotspot.\n")
    print("  Pairing code:", pairing.code)
    print("  The host monitors private adapters and adds USB tethering addresses after startup.")
    print("  Initial local addresses (may change when USB tethering starts):")
    for ip in bind_addresses(discover_lan_ips()):
        print(f"    http://{ip}:{args.port}")
    try:
        available = list_monitors()
        print("  Windows monitors:", available)
        if not any(m["index"] == args.monitor for m in available):
            print(f"  Monitor {args.monitor} not found; restart with --monitor INDEX")
    except Exception as exc:
        print(f"  Display capture warning: {exc}")
    print("  For Android, use Find SuperScreen Host, or enter the private host IP.")
    print("  No independent virtual display, secure Windows login or input control yet.")
    print("  Press Ctrl+C to stop.\n")

    app = create_app(
        pairing, monitor=args.monitor, fps=args.fps,
        max_width=args.max_width, quality=args.quality,
    )
    try:
        asyncio.run(serve_watched(app, args.port))
    except KeyboardInterrupt:
        print("  SuperScreen host stopped.")


if __name__ == "__main__":
    main()
