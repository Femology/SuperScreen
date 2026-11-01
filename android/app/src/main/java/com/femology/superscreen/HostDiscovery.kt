package com.femology.superscreen

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.Inet4Address
import java.net.NetworkInterface
import java.net.URL
import java.util.concurrent.Callable
import java.util.concurrent.ExecutorCompletionService
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.TimeUnit

/**
 * User-initiated discovery of our *own* SuperScreen host on a trusted USB-tether
 * or phone-hotspot subnet. This does not connect to SuperDisplay's driver.
 *
 * No cloud, third-party analytics, credentials, or broadcast traffic. Discovery
 * checks only RFC1918 /24 neighbours of a local USB/Wi-Fi interface on TCP 8765.
 * The authenticated viewer still requires pairing after a host is found.
 */
internal object HostDiscovery {
    private const val PORT = 8765
    private const val TIMEOUT_MS = 450
    private const val TOTAL_TIMEOUT_MS = 10_000L

    fun findWindowsHost(): String? {
        val prefixes = interfacePrefixes().take(2)
        if (prefixes.isEmpty()) return null
        val executor = Executors.newFixedThreadPool(24)
        val completion = ExecutorCompletionService<String?>(executor)
        val pending = mutableListOf<Future<String?>>()
        val deadline = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(TOTAL_TIMEOUT_MS)
        var total = 0

        try {
            for (prefix in prefixes) {
                // Common DHCP assignments first; the remaining range follows.
                val suffixes = (100..150).toList() + (2..99).toList() + (151..254).toList() + listOf(1)
                for (suffix in suffixes) {
                    val host = "$prefix$suffix"
                    total++
                    pending.add(completion.submit(Callable {
                        if (Thread.currentThread().isInterrupted) null else probe(host)
                    }))
                }
            }
            repeat(total) {
                val left = deadline - System.nanoTime()
                if (left <= 0L) return null
                val done = completion.poll(left, TimeUnit.NANOSECONDS) ?: return null
                val found = done.get()
                if (found != null) return found
            }
            return null
        } catch (_: InterruptedException) {
            Thread.currentThread().interrupt()
            return null
        } catch (_: Exception) {
            return null
        } finally {
            pending.forEach { it.cancel(true) }
            executor.shutdownNow()
        }
    }

    internal fun localPrefix(interfaceName: String, address: String): String? {
        val name = interfaceName.lowercase()
        if (!(name.startsWith("rndis") || name.startsWith("usb") ||
                name.startsWith("ncm") || name.startsWith("ap") ||
                name.startsWith("wlan") || name.startsWith("eth"))) return null
        val octets = address.split('.').mapNotNull { it.toIntOrNull() }
        if (octets.size != 4 || octets.any { it !in 0..255 }) return null
        val privateAddress = octets[0] == 10 ||
            (octets[0] == 172 && octets[1] in 16..31) ||
            (octets[0] == 192 && octets[1] == 168)
        if (!privateAddress) return null
        // /24 is a heuristic, not a guarantee about the adapter's actual netmask.
        return "${octets[0]}.${octets[1]}.${octets[2]}."
    }

    private fun interfacePrefixes(): List<String> {
        return try {
            val out = linkedSetOf<String>()
            val interfaces = NetworkInterface.getNetworkInterfaces() ?: return emptyList()
            while (interfaces.hasMoreElements()) {
                val nic = interfaces.nextElement()
                if (!nic.isUp || nic.isLoopback) continue
                val addresses = nic.inetAddresses
                while (addresses.hasMoreElements()) {
                    val ip = addresses.nextElement()
                    if (ip is Inet4Address) {
                        localPrefix(nic.name, ip.hostAddress ?: "")?.let(out::add)
                    }
                }
            }
            out.toList()
        } catch (_: Exception) {
            emptyList()
        }
    }

    private fun probe(host: String): String? {
        var conn: HttpURLConnection? = null
        return try {
            conn = URL("http://$host:$PORT/api/status").openConnection() as HttpURLConnection
            conn.requestMethod = "GET"
            conn.connectTimeout = TIMEOUT_MS
            conn.readTimeout = TIMEOUT_MS
            conn.instanceFollowRedirects = false
            if (conn.responseCode != 200) return null
            val json = conn.inputStream.bufferedReader().use { it.readText() }
            val metadata = JSONObject(json)
            if (metadata.optString("name") == "SuperScreen" &&
                metadata.optString("mode") == "mirror") host else null
        } catch (_: Exception) {
            null
        } finally {
            conn?.disconnect()
        }
    }
}
