package com.femology.superscreen

import android.app.Activity
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.view.ViewGroup
import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.WebResourceRequest
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

/**
 * Native Android launcher for the experimental browser-based viewer.
 * View-only over local HTTP: not a true second monitor, MediaCodec decoder,
 * unattended hotspot controller, or production-secure remote desktop.
 */
class MainActivity : Activity() {
    private var viewer: WebView? = null
    private val prefs by lazy { getSharedPreferences("superscreen", MODE_PRIVATE) }
    private val background = Color.rgb(9, 11, 17)
    private val foreground = Color.rgb(244, 247, 255)
    private val muted = Color.rgb(154, 169, 191)
    private val accent = Color.rgb(145, 136, 255)

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
    private fun rounded(color: Int): GradientDrawable = GradientDrawable().apply {
        setColor(color)
        cornerRadius = dp(14).toFloat()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = background
        window.navigationBarColor = background
        showHome()
    }

    private fun text(value: String, size: Float, color: Int, bold: Boolean = false) =
        TextView(this).apply {
            text = value
            textSize = size
            setTextColor(color)
            if (bold) setTypeface(typeface, Typeface.BOLD)
        }

    private fun addButton(root: LinearLayout, title: String, highlight: Boolean, click: () -> Unit) {
        val button = Button(this).apply {
            text = title
            isAllCaps = false
            setTextColor(if (highlight) Color.BLACK else foreground)
            background = rounded(if (highlight) accent else Color.rgb(30, 36, 49))
            setOnClickListener { click() }
        }
        root.addView(button, LinearLayout.LayoutParams(-1, dp(52)).apply { topMargin = dp(12) })
    }

    private fun showHome() {
        viewer?.destroy()
        viewer = null
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(24), dp(24), dp(24), dp(24))
            setBackgroundColor(background)
        }
        setContentView(ScrollView(this).apply { addView(root) })
        root.addView(text("▣  SUPERSCREEN", 16f, accent, true))
        root.addView(text("One computer.\nEvery screen.", 33f, foreground, true).apply {
            setPadding(0, dp(35), 0, dp(20))
        })
        root.addView(text(
            "Use your phone's own hotspot, connect Windows to it, then view your Windows screen directly on this phone. No router or second phone.",
            15f, muted
        ))
        root.addView(text("WINDOWS HOST IPv4 ADDRESS", 12f, accent, true).apply {
            setPadding(0, dp(36), 0, dp(9))
        })
        val address = EditText(this).apply {
            hint = "192.168.43.102"
            setSingleLine(true)
            setTextColor(foreground)
            setHintTextColor(muted)
            inputType = android.text.InputType.TYPE_CLASS_TEXT
            background = rounded(Color.rgb(23, 29, 42))
            setPadding(dp(16), dp(12), dp(16), dp(12))
            setText(prefs.getString("host", ""))
        }
        root.addView(address, LinearLayout.LayoutParams(-1, dp(54)))
        addButton(root, "CONNECT TO WINDOWS →", true) {
            val value = address.text.toString().trim()
            if (!validPrivateIPv4(value)) {
                address.error = "Enter a private IPv4 address from Windows PowerShell"
            } else {
                prefs.edit().putString("host", value).apply()
                showViewer(value)
            }
        }
        addButton(root, "OPEN PHONE NETWORK SETTINGS", false) {
            startActivity(Intent(Settings.ACTION_WIRELESS_SETTINGS))
        }
        root.addView(text(
            "For first setup, the Windows PC must run the SuperScreen host. Enter the six-digit pairing code shown in its terminal. Subsequent sessions remember the connection address.",
            13f, muted
        ).apply { setPadding(0, dp(30), 0, 0) })
        root.addView(text(
            "ALPHA SECURITY WARNING: unencrypted screen stream. Only use with your own trusted phone hotspot.",
            12f, Color.rgb(248, 151, 165), true
        ).apply { setPadding(0, dp(28), 0, 0) })
    }

    private fun validPrivateIPv4(s: String): Boolean {
        if (!s.matches(Regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}$"))) return false
        val values = s.split('.').mapNotNull { it.toIntOrNull() }
        if (values.size != 4 || values.any { it > 255 || it < 0 }) return false
        return values[0] == 10 ||
            (values[0] == 172 && values[1] in 16..31) ||
            (values[0] == 192 && values[1] == 168)
    }

    private fun showViewer(host: String) {
        val outer = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(background)
        }
        val header = LinearLayout(this).apply {
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(10), 0, dp(10), 0)
        }
        addButton(header, "← Change PC", false) { showHome() }
        outer.addView(header, LinearLayout.LayoutParams(-1, dp(63)))
        val web = WebView(this).apply {
            setBackgroundColor(background)
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
        viewer?.destroy()
        viewer = null
        super.onDestroy()
    }
}
