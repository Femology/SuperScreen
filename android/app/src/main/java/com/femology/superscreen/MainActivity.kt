package com.femology.superscreen

import android.app.Activity
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import kotlin.concurrent.thread

/**
 * First-party Android receiver for the experimental SuperScreen Windows host.
 * USB tethering / own-phone hotspot use ordinary TCP, NOT SuperDisplay USB.
 *
 * The current host mirrors an existing Windows display. A separate Windows
 * Indirect Display Driver (IDD) is needed for a true extended virtual monitor.
 */
class MainActivity : Activity() {
    private var viewer: WebView? = null
    private val prefs by lazy { getSharedPreferences("superscreen", MODE_PRIVATE) }
    private var discoveryGeneration = 0
    private var discovering = false
    private val backdropColor = Color.rgb(8, 9, 10)
    private val inkColor = Color.rgb(239, 238, 231)
    private val muted = Color.rgb(161, 166, 159)
    private val accent = Color.rgb(227, 250, 97)

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
    private fun rounded(color: Int): GradientDrawable = GradientDrawable().apply {
        setColor(color)
        cornerRadius = dp(14).toFloat()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = backdropColor
        window.navigationBarColor = backdropColor
        val remembered = prefs.getString("host", null)
        if (remembered != null && validPrivateIPv4(remembered)) {
            showViewer(remembered)
        } else {
            showHome()
        }
    }

    private fun text(value: String, size: Float, color: Int, bold: Boolean = false) =
        TextView(this).apply {
            text = value
            textSize = size
            setTextColor(color)
            if (bold) setTypeface(typeface, Typeface.BOLD)
        }

    private fun button(title: String, highlight: Boolean, click: () -> Unit): Button =
        Button(this).apply {
            text = title
            isAllCaps = false
            setTextColor(if (highlight) Color.BLACK else inkColor)
            background = rounded(if (highlight) accent else Color.rgb(28, 30, 29))
            setOnClickListener { click() }
        }

    private fun addButton(root: LinearLayout, title: String, highlight: Boolean, click: () -> Unit) {
        root.addView(button(title, highlight, click),
            LinearLayout.LayoutParams(-1, dp(52)).apply { topMargin = dp(12) })
    }

    private fun immersive(enabled: Boolean) {
        @Suppress("DEPRECATION")
        window.decorView.systemUiVisibility = if (enabled) (
            View.SYSTEM_UI_FLAG_FULLSCREEN or
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        ) else 0
    }

    private fun showHome(message: String? = null) {
        discoveryGeneration++ // Discard callbacks from any prior discovery screen.
        immersive(false)
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        viewer?.destroy()
        viewer = null
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(24), dp(24), dp(24), dp(24))
            setBackgroundColor(backdropColor)
        }
        setContentView(ScrollView(this).apply { addView(root) })
        root.addView(text("▣   SUPER/SCREEN", 15f, accent, true))
        root.addView(text("Your Windows.\\nYour phone.", 33f, inkColor, true).apply {
            setPadding(0, dp(35), 0, dp(20))
        })
        root.addView(text(
            "Use your own hotspot or a USB-tethered connection. Only the locally installed SuperScreen Windows host can connect.",
            15f, muted
        ))
        root.addView(text("01 / FIND THE COMPUTER", 12f, accent, true).apply {
            setPadding(0, dp(28), 0, dp(9))
        })
        val searchStatus = text(
            message ?: "Connect USB and enable USB tethering, or turn on your phone hotspot and join it from Windows.",
            13f, muted
        )
        addButton(root, "FIND SUPER/SCREEN HOST", true) {
            if (!discovering) {
                discovering = true
                searchStatus.text = "Searching your own USB / Wi-Fi subnet for SuperScreen…"
                val current = ++discoveryGeneration
                thread(name = "superscreen-local-discovery", isDaemon = true) {
                    val host = HostDiscovery.findWindowsHost()
                    runOnUiThread {
                        if (isFinishing || isDestroyed || current != discoveryGeneration) return@runOnUiThread
                        discovering = false
                        if (host == null) {
                            searchStatus.text = "No SuperScreen host found. Confirm the Windows host is running, the USB tether or private hotspot is active, and Windows firewall permits TCP 8765."
                        } else {
                            prefs.edit().putString("host", host).apply()
                            showViewer(host)
                        }
                    }
                }
            }
        }
        root.addView(searchStatus.apply { setPadding(0, dp(14), 0, dp(12)) })
        addButton(root, "OPEN USB TETHERING / NETWORK SETTINGS", false) {
            startActivity(Intent(Settings.ACTION_WIRELESS_SETTINGS))
        }
        root.addView(text("02 / OR ENTER WINDOWS ADDRESS", 12f, accent, true).apply {
            setPadding(0, dp(28), 0, dp(9))
        })
        val address = EditText(this).apply {
            hint = "192.168.42.101"
            setSingleLine(true)
            setTextColor(inkColor)
            setHintTextColor(muted)
            inputType = android.text.InputType.TYPE_CLASS_TEXT
            background = rounded(Color.rgb(22, 24, 23))
            setPadding(dp(16), dp(12), dp(16), dp(12))
            setText(prefs.getString("host", ""))
        }
        root.addView(address, LinearLayout.LayoutParams(-1, dp(54)))
        addButton(root, "CONNECT MANUALLY", false) {
            val value = address.text.toString().trim()
            if (!validPrivateIPv4(value)) {
                address.error = "Enter the private IPv4 address shown by the Windows host"
            } else {
                prefs.edit().putString("host", value).apply()
                showViewer(value)
            }
        }
        root.addView(text(
            "The Windows host must already be installed and running. It will ask you for a six-digit pairing code on first use. USB tethering is not the proprietary SuperDisplay accessory connection.",
            13f, muted
        ).apply { setPadding(0, dp(28), 0, 0) })
        root.addView(text(
            "PREVIEW / Unencrypted local transport. Use only your private USB link or protected hotspot.",
            12f, Color.rgb(248, 151, 165), true
        ).apply { setPadding(0, dp(25), 0, 0) })
    }

    private fun validPrivateIPv4(s: String): Boolean {
        if (!s.matches(Regex("^([0-9]{1,3}\\\\.){3}[0-9]{1,3}$"))) return false
        val values = s.split('.').mapNotNull { it.toIntOrNull() }
        if (values.size != 4 || values.any { it > 255 || it < 0 }) return false
        return values[0] == 10 ||
            (values[0] == 172 && values[1] in 16..31) ||
            (values[0] == 192 && values[1] == 168)
    }

    private fun showViewer(host: String) {
        discovering = false
        discoveryGeneration++
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        val outer = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(backdropColor)
        }
        val header = LinearLayout(this).apply {
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(8), dp(6), dp(8), dp(6))
        }
        header.addView(button("← Change PC", false) { showHome() },
            LinearLayout.LayoutParams(0, dp(48), 1f))
        header.addView(button("Full screen", false) { immersive(true) },
            LinearLayout.LayoutParams(0, dp(48), 1f).apply { leftMargin = dp(8) })
        outer.addView(header, LinearLayout.LayoutParams(-1, dp(62)))
        viewer?.destroy()
        val web = WebView(this).apply {
            setBackgroundColor(backdropColor)
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                    val url = request.url
                    return !(url.scheme == "http" && url.host == host && url.port == 8765)
                }
            }
        }
        viewer = web
        outer.addView(web, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f
        ))
        setContentView(outer)
        web.loadUrl("http://$host:8765/")
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (viewer != null) showHome() else super.onBackPressed()
    }

    override fun onDestroy() {
        discoveryGeneration++
        viewer?.destroy()
        viewer = null
        super.onDestroy()
    }
}
