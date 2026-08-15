package cn.lasa.fieldapp

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.webkit.GeolocationPermissions
import android.webkit.JavascriptInterface
import android.webkit.PermissionRequest
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import java.io.File

/**
 * 南北山外业调查 App：WebView 混合壳。
 *  - 加载平台移动端野外科考页（拍照/录像、样地注释、媒体库、轨迹展示）
 *  - 通过 AndroidBridge 向网页暴露原生后台轨迹服务（熄屏持续记录）
 *  - WebView 内定位/相机授权自动打通（HTTP 页面浏览器限制在壳内不生效）
 */
class MainActivity : Activity() {

    companion object {
        const val BASE_URL = "http://106.15.35.204:18480/m"
        const val REQ_PERMS = 1001
        const val REQ_FILE = 1002
    }

    private lateinit var webView: WebView
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private var cameraUri: Uri? = null

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        webView = WebView(this)
        setContentView(webView)

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            allowFileAccess = true
            mediaPlaybackRequiresUserGesture = false
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            setGeolocationEnabled(true)
            loadWithOverviewMode = true
            useWideViewPort = true
            builtInZoomControls = false
        }
        webView.webViewClient = object : WebViewClient() {}
        webView.webChromeClient = object : WebChromeClient() {
            // 网页请求定位 → 已授予系统权限则直接放行
            override fun onGeolocationPermissionsShowPrompt(origin: String?, callback: GeolocationPermissions.Callback?) {
                callback?.invoke(origin, hasLocationPermission(), false)
            }

            // <input type=file> → 按网页参数分流：拍照直启相机 / 录像直启摄像 / 相册支持多选
            override fun onShowFileChooser(wv: WebView?, cb: ValueCallback<Array<Uri>>?, params: FileChooserParams?): Boolean {
                fileCallback?.onReceiveValue(null)
                fileCallback = cb
                val accept = params?.acceptTypes?.filter { it.isNotBlank() } ?: emptyList()
                val capture = params?.isCaptureEnabled == true
                val multi = params?.mode == FileChooserParams.MODE_OPEN_MULTIPLE
                return openPicker(accept, capture, multi)
            }

            // 网页请求摄像头/麦克风权限（getUserMedia）→ 壳内直接授予（内容可信）
            override fun onPermissionRequest(request: PermissionRequest?) {
                runOnUiThread { request?.grant(request.resources) }
            }
        }
        webView.addJavascriptInterface(AppBridge(), "AndroidBridge")

        requestNeededPermissions()
        if (savedInstanceState != null) webView.restoreState(savedInstanceState) else webView.loadUrl(BASE_URL)
    }

    private fun hasLocationPermission(): Boolean =
        ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED

    private fun requestNeededPermissions() {
        val perms = mutableListOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.CAMERA,
        )
        if (Build.VERSION.SDK_INT >= 33) perms.add(Manifest.permission.POST_NOTIFICATIONS)
        val lacking = perms.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (lacking.isNotEmpty()) {
            androidx.core.app.ActivityCompat.requestPermissions(this, lacking.toTypedArray(), REQ_PERMS)
        }
    }

    /** 打开「拍照 / 录像 / 相册」选择器：capture 时直启相机；相册按 accept 限定类型并支持多选 */
    private fun openPicker(accept: List<String>, capture: Boolean, allowMulti: Boolean): Boolean {
        return try {
            val wantVideo = accept.any { it.startsWith("video") }
            val wantImage = accept.any { it.startsWith("image") }
            val onlyExt = accept.isNotEmpty() && accept.all { it.startsWith(".") }
            val dir = File(cacheDir, "camera").apply { mkdirs() }
            val ext = if (wantVideo && !wantImage) ".mp4" else ".jpg"
            cameraUri = FileProvider.getUriForFile(this, "cn.lasa.fieldapp.fileprovider",
                File(dir, "capture_${System.currentTimeMillis()}$ext"))
            val shoot = Intent(if (wantVideo && !wantImage) MediaStore.ACTION_VIDEO_CAPTURE else MediaStore.ACTION_IMAGE_CAPTURE).apply {
                putExtra(MediaStore.EXTRA_OUTPUT, cameraUri)
                addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION or Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            if (capture) {  // 网页 input 带 capture 属性：直启拍摄，不弹选择器
                startActivityForResult(shoot, REQ_FILE)
                return true
            }
            val content = Intent(Intent.ACTION_GET_CONTENT).apply {
                addCategory(Intent.CATEGORY_OPENABLE)
                when {
                    onlyExt || accept.isEmpty() -> type = "*/*"
                    wantImage && wantVideo -> {
                        type = "*/*"
                        putExtra(Intent.EXTRA_MIME_TYPES, arrayOf("image/*", "video/*"))
                    }
                    wantVideo -> type = "video/*"
                    else -> type = "image/*"
                }
                putExtra(Intent.EXTRA_ALLOW_MULTIPLE, allowMulti)
            }
            val chooser = Intent(Intent.ACTION_CHOOSER).apply {
                putExtra(Intent.EXTRA_INTENT, content)
                if (!onlyExt) putExtra(Intent.EXTRA_INITIAL_INTENTS, arrayOf(shoot))
                putExtra(Intent.EXTRA_TITLE, "拍照/拍摄或选择文件")
            }
            startActivityForResult(chooser, REQ_FILE)
            true
        } catch (e: Exception) {
            fileCallback = null
            false
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQ_FILE) {
            val cb = fileCallback ?: return
            fileCallback = null
            if (resultCode != RESULT_OK) { cb.onReceiveValue(null); return }
            val uris = mutableListOf<Uri>()
            data?.clipData?.let { clip -> for (i in 0 until clip.itemCount) uris.add(clip.getItemAt(i).uri) }
            if (uris.isEmpty()) data?.data?.let { uris.add(it) }
            if (uris.isEmpty()) cameraUri?.let { uris.add(it) }  // 相机拍摄返回
            cb.onReceiveValue(uris.toTypedArray())
            return
        }
        if (requestCode == REQ_PERMS && !hasLocationPermission()) {
            Toast.makeText(this, "未授予定位权限，轨迹记录将不可用", Toast.LENGTH_LONG).show()
        }
    }

    override fun onBackPressed() {
        if (this::webView.isInitialized && webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        if (this::webView.isInitialized) webView.saveState(outState)
    }

    /** 暴露给网页的原生能力（window.AndroidBridge.*） */
    inner class AppBridge {
        @JavascriptInterface
        fun isApp(): Boolean = true

        @JavascriptInterface
        fun appVersion(): String = "1.2.0"

        @JavascriptInterface
        fun startTrack(): String {
            if (!hasLocationPermission()) {
                requestNeededPermissions()
                return "{\"ok\":false,\"msg\":\"缺少定位权限，请在系统弹窗中允许\"}"
            }
            val i = Intent(this@MainActivity, TrackService::class.java).setAction(TrackService.ACTION_START)
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(i) else startService(i)
            return "{\"ok\":true}"
        }

        @JavascriptInterface
        fun stopTrack(): String {
            val i = Intent(this@MainActivity, TrackService::class.java).setAction(TrackService.ACTION_STOP)
            startService(i)
            return TrackService.stopJson()
        }

        @JavascriptInterface
        fun getStatus(): String = TrackService.statusJson()
    }
}
