package com.femology.superscreen

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class HostDiscoveryTest {
    @Test fun acceptsUsbTetherAddress() {
        assertEquals("192.168.42.", HostDiscovery.localPrefix("rndis0", "192.168.42.129"))
        assertEquals("172.20.10.", HostDiscovery.localPrefix("usb0", "172.20.10.1"))
        assertEquals("10.23.4.", HostDiscovery.localPrefix("ncm0", "10.23.4.1"))
    }

    @Test fun acceptsPhoneHotspotAddress() {
        assertEquals("192.168.43.", HostDiscovery.localPrefix("ap0", "192.168.43.1"))
        assertEquals("192.168.232.", HostDiscovery.localPrefix("wlan0", "192.168.232.1"))
    }

    @Test fun refusesNonlocalAndVpnInterfaces() {
        assertNull(HostDiscovery.localPrefix("tun0", "192.168.42.1"))
        assertNull(HostDiscovery.localPrefix("rmnet_data0", "10.1.1.1"))
        assertNull(HostDiscovery.localPrefix("usb0", "8.8.8.8"))
        assertNull(HostDiscovery.localPrefix("rndis0", "169.254.1.5"))
        assertNull(HostDiscovery.localPrefix("rndis0", "192.168.42.999"))
        assertNull(HostDiscovery.localPrefix("rndis0", "not-an-ip"))
    }
}
