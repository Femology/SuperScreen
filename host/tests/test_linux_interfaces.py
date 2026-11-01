"""Read-only Linux interface discovery for USB-tether testing."""
from __future__ import annotations

import json
from types import SimpleNamespace

from superscreen import network


def test_linux_private_usb_tether_address(monkeypatch):
    interfaces = [
        {"ifname": "lo", "addr_info": [{"family": "inet", "local": "127.0.0.1"}]},
        {"ifname": "enx2aa", "addr_info": [
            {"family": "inet", "local": "192.168.42.102", "prefixlen": 24}]},
        {"ifname": "wlp0s20f3", "addr_info": [
            {"family": "inet", "local": "10.20.30.55", "prefixlen": 24}]},
        {"ifname": "eth0", "addr_info": [{"family": "inet", "local": "8.8.8.8"}]},
        {"ifname": "ignored", "addr_info": [{"family": "inet6", "local": "fe80::1"}]},
    ]
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["timeout"] = kwargs["timeout"]
        return SimpleNamespace(returncode=0, stdout=json.dumps(interfaces))

    monkeypatch.setattr(network.sys, "platform", "linux")
    monkeypatch.setattr(network.subprocess, "run", fake_run)
    found = network._linux_adapter_ipv4s()
    assert found == {"192.168.42.102", "10.20.30.55"}
    assert captured["command"] == ["ip", "-j", "-4", "addr", "show"]
    assert captured["timeout"] <= 3


def test_linux_address_fails_closed_when_command_unavailable(monkeypatch):
    monkeypatch.setattr(network.sys, "platform", "linux")

    def unavailable(*args, **kwargs):
        raise FileNotFoundError("ip not installed")

    monkeypatch.setattr(network.subprocess, "run", unavailable)
    assert network._linux_adapter_ipv4s() == set()


def test_linux_address_rejects_malformed_json(monkeypatch):
    monkeypatch.setattr(network.sys, "platform", "linux")
    monkeypatch.setattr(network.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0, stdout="[invalid"))
    assert network._linux_adapter_ipv4s() == set()


def test_non_linux_hosts_do_not_launch_ip_tool(monkeypatch):
    monkeypatch.setattr(network.sys, "platform", "win32")
    monkeypatch.setattr(network.subprocess, "run", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("called")))
    assert network._linux_adapter_ipv4s() == set()
