"""The preview host must survive USB-tether adapter hotplug, without wildcard binding."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from superscreen import listener, network


def test_windows_adapter_enumeration(monkeypatch):
    seen = {}

    def fake_run(command, **kwargs):
        seen["command"] = command
        seen["timeout"] = kwargs["timeout"]
        return SimpleNamespace(returncode=0, stdout="192.168.42.101\n8.8.8.8\n")

    with monkeypatch.context() as patch:
        patch.setattr(network.sys, "platform", "win32")
        patch.setattr(network.subprocess, "run", fake_run)
        addresses = network._windows_adapter_ipv4s()
    assert "192.168.42.101" in addresses
    assert seen["timeout"] <= 5
    assert seen["command"][0] == "powershell.exe"
    assert network.bind_addresses(list(addresses)) == ["127.0.0.1", "192.168.42.101"]


@pytest.mark.asyncio
async def test_private_interfaces_added_and_removed_after_usb_hotplug(monkeypatch):
    current = [["192.168.43.10"]]
    recorded = {}

    class FakeRunner:
        def __init__(self, app, **kwargs): pass
        async def setup(self): recorded["runner_started"] = True
        async def cleanup(self): recorded["runner_stopped"] = True

    class FakeSite:
        def __init__(self, runner, *, host, port):
            self.host, self.port = host, port
        async def start(self): recorded[f"started:{self.host}"] = True
        async def stop(self): recorded[f"stopped:{self.host}"] = True

    monkeypatch.setattr(listener.web, "AppRunner", FakeRunner)
    monkeypatch.setattr(listener.web, "TCPSite", FakeSite)
    monkeypatch.setattr(listener, "discover_lan_ips", lambda: list(current[0]))
    service = listener.PrivateInterfaceListener(object(), 8765)
    await service.start()
    assert set(service.sites) == {"127.0.0.1", "192.168.43.10"}

    current[0] = ["192.168.43.10", "192.168.42.101"]
    await service.refresh()
    assert "192.168.42.101" in service.sites
    assert recorded["started:192.168.42.101"]

    current[0] = ["192.168.42.101"]
    await service.refresh()
    assert "192.168.43.10" not in service.sites
    assert recorded["stopped:192.168.43.10"]

    await service.close()
    assert recorded["runner_stopped"]


def test_private_listener_validates_options():
    with pytest.raises(ValueError):
        listener.PrivateInterfaceListener(object(), 0)
    with pytest.raises(ValueError):
        listener.PrivateInterfaceListener(object(), 8765, poll_seconds=0)
