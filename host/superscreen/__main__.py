"""Start the local SuperScreen proof of concept on a Windows host."""
from __future__ import annotations

import argparse
import sys

from aiohttp import web

from .auth import PairingManager
from .capture import list_monitors
from .network import discover_lan_ips, bind_addresses
from .server import create_app


def main() -> None:
    p = argparse.ArgumentParser(description="SuperScreen trusted-hotspot mirroring prototype")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--monitor", type=int, default=1, help="Physical monitor index (TV may be 2)")
    p.add_argument("--fps", type=float, default=8, help="1-15; keep low on older laptops")
    p.add_argument("--max-width", type=int, default=960, help="JPEG frame width 160-3840")
    p.add_argument("--quality", type=int, default=60, help="JPEG quality 20-95")
    args = p.parse_args()

    if sys.platform != "win32":
        print("Warning: developed for Windows; other systems are not yet validated.")
    if not (1 <= args.port <= 65535 and 160 <= args.max_width <= 3840 and 20 <= args.quality <= 95):
        p.error("Invalid port, width or quality")
    pairing = PairingManager()
    print("\n  SuperScreen 0.1 — experimental mirror over your own phone hotspot")
    print("  WARNING: unencrypted local traffic. Use only a trusted private hotspot.\n")
    print("  Pairing code:", pairing.code)
    print("  Open one of these addresses ON YOUR PHONE (while hotspot is on):")
    private_ips = discover_lan_ips()
    for ip in private_ips:
        print(f"    http://{ip}:{args.port}")
    print(f"    http://127.0.0.1:{args.port}  (this PC only)")
    print("  If no hotspot address appears, run 'ipconfig' and use the laptop Wi-Fi IPv4 address.")
    try:
        available = list_monitors()
        print("  Windows monitors:", available)
        if not any(m["index"] == args.monitor for m in available):
            print(f"  Monitor {args.monitor} not found. Restart with --monitor INDEX")
    except Exception as exc:
        print(f"  Display capture warning: {exc}")
    print("  Keep this window open. Press Ctrl+C to stop.\n")

    app = create_app(
        pairing, monitor=args.monitor, fps=args.fps,
        max_width=args.max_width, quality=args.quality,
    )
    # The port is exposed on the phone's local network to support phone-as-hotspot.
    # Firewall should allow only Private networks.
    hosts = bind_addresses(private_ips)
    if len(hosts) == 1:
        print("  No private IPv4 address detected. Turn on the phone hotspot, connect Windows, and restart.")
    print("  Listening only on:", ", ".join(hosts))
    web.run_app(app, host=hosts, port=args.port, print=None)


if __name__ == "__main__":
    main()
