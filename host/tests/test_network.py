import pytest

from superscreen.network import is_usable_private_ip, is_permitted_remote, bind_addresses


@pytest.mark.parametrize("ip", ["192.168.43.20", "172.20.10.2", "10.1.1.2"])
def test_private_hotspot_addresses(ip):
    assert is_usable_private_ip(ip)


@pytest.mark.parametrize("ip", ["127.0.0.1", "169.254.1.1", "0.0.0.0", "8.8.8.8", "255.255.255.255", "::1", "nonsense"])
def test_reject_non_private_address(ip):
    assert not is_usable_private_ip(ip)


@pytest.mark.parametrize("ip,allowed", [
    ("127.0.0.1", True), ("::1", True), ("192.168.43.1", True),
    ("172.20.10.2", True), ("10.1.1.1", True),
    ("8.8.8.8", False), ("1.1.1.1", False),
    ("255.255.255.255", False), ("not-an-ip", False),
])
def test_only_local_private_clients_can_pair(ip, allowed):
    assert is_permitted_remote(ip) == allowed


def test_bind_private_adapters_only():
    assert bind_addresses(["192.168.43.15", "8.8.8.8", "10.0.0.1", "10.0.0.1"]) == [
        "127.0.0.1", "10.0.0.1", "192.168.43.15"
    ]
    assert bind_addresses([]) == ["127.0.0.1"]
