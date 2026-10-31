import pytest

from superscreen.network import is_usable_private_ip


@pytest.mark.parametrize("ip", ["192.168.43.20", "172.20.10.2", "10.1.1.2"])
def test_private_hotspot_addresses(ip):
    assert is_usable_private_ip(ip)


@pytest.mark.parametrize("ip", ["127.0.0.1", "169.254.1.1", "0.0.0.0", "8.8.8.8", "255.255.255.255", "::1", "nonsense"])
def test_reject_non_private_address(ip):
    assert not is_usable_private_ip(ip)
