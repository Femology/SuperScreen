"""Discover private interfaces, including Windows USB-tether adapters.

Never bind the unencrypted preview to a public interface or 0.0.0.0.
"""
from __future__ import annotations

import ipaddress
import json
import socket
import subprocess
import sys


def is_usable_private_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return (
        isinstance(ip, ipaddress.IPv4Address)
        and any(ip in network for network in (
            ipaddress.ip_network("10.0.0.0/8"),
            ipaddress.ip_network("172.16.0.0/12"),
            ipaddress.ip_network("192.168.0.0/16"),
        ))
        and not (ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified)
    )


def _windows_adapter_ipv4s() -> set[str]:
    """Enumerate USB/RNDIS and other adapters without admin rights.

    hostname DNS alone often misses tethered adapters. Keep a short timeout,
    never interpolate user input into PowerShell, and fail closed.
    """
    if sys.platform != "win32":
        return set()
    cmd = (
        "Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue "
        "| Select-Object -ExpandProperty IPAddress"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=5, check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.TimeoutExpired):
        return set()
    return set(result.stdout.splitlines()) if result.returncode == 0 else set()



def _linux_adapter_ipv4s() -> set[str]:
    """Read assigned Linux interface addresses (including USB/RNDIS tethering).

    Hostname lookup on Ubuntu often resolves to loopback only. iproute2's
    JSON output provides the assigned local addresses without requiring sudo.
    No external network probes, daemon writes, or privileges are used.
    """
    if not sys.platform.startswith("linux"):
        return set()
    try:
        result = subprocess.run(
            ["ip", "-j", "-4", "addr", "show"],
            capture_output=True, text=True, timeout=3, check=False,
        )
        if result.returncode != 0:
            return set()
        adapters = json.loads(result.stdout)
        if not isinstance(adapters, list):
            return set()
        ips: set[str] = set()
        for adapter in adapters:
            if not isinstance(adapter, dict):
                continue
            for address in adapter.get("addr_info", []):
                if isinstance(address, dict) and address.get("family") == "inet":
                    local = address.get("local")
                    if isinstance(local, str) and is_usable_private_ip(local):
                        ips.add(local)
        return ips
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired):
        return set()


def discover_lan_ips() -> list[str]:
    values: set[str] = set()
    try:
        values.update(socket.gethostbyname_ex(socket.gethostname())[2])
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            values.add(info[4][0])
    except OSError:
        pass
    # A UDP connect selects a local outgoing address but sends no packet.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.0.2.1", 1))
            values.add(sock.getsockname()[0])
    except OSError:
        pass
    values.update(_windows_adapter_ipv4s())
    values.update(_linux_adapter_ipv4s())
    return sorted(
        (ip for ip in values if is_usable_private_ip(ip)),
        key=lambda ip: tuple(map(int, ip.split("."))),
    )


def is_permitted_remote(value: str) -> bool:
    """Only local loopback and RFC1918 peers may reach the preview host."""
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return bool(ip.is_loopback or is_usable_private_ip(value))


def bind_addresses(private_ips: list[str]) -> list[str]:
    """Explicit per-interface binding; never wildcard to 0.0.0.0."""
    return ["127.0.0.1", *sorted(set(
        ip for ip in private_ips if is_usable_private_ip(ip)
    ))]
