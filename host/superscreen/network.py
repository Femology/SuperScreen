"""Find likely LAN addresses for the phone hotspot; no internet request is made."""
from __future__ import annotations

import ipaddress
import socket


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


def discover_lan_ips() -> list[str]:
    values: set[str] = set()
    try:
        values.update(socket.gethostbyname_ex(socket.gethostname())[2])
    except OSError:
        pass
    # UDP connect chooses the local outgoing address but transmits no packet.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.0.2.1", 1))
            values.add(sock.getsockname()[0])
    except OSError:
        pass
    return sorted((ip for ip in values if is_usable_private_ip(ip)), key=lambda ip: tuple(map(int, ip.split("."))))


def is_permitted_remote(value: str) -> bool:
    """Only local loopback and RFC1918 peers should reach the alpha host."""
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return bool(ip.is_loopback or is_usable_private_ip(value))


def bind_addresses(private_ips: list[str]) -> list[str]:
    """Bind only to local private addresses instead of every public interface."""
    return ["127.0.0.1", *sorted(set(
        value for value in private_ips if is_usable_private_ip(value)
    ))]
