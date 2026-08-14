package cn.lasa.fieldapp

import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Build
import android.os.Bundle
import android.os.IBinder
import android.os.PowerManager
import androidx.core.content.ContextCompat
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import java.util.concurrent.CopyOnWriteArrayList

/**
 * 外业轨迹前台服务：GPS + 网络双源供点，部分唤醒锁保证熄屏持续记录。
 * 状态保存在伴生对象（与网页 JS 桥同进程共享），无需 Binder。
 */
class TrackService : Service(), LocationListener {

    data class TrackPoint(val lat: Double, val lon: Double, val alt: Double?, val time: String)

    companion object {
        const val ACTION_START = "cn.lasa.fieldapp.action.START"
        const val ACTION_STOP = "cn.lasa.fieldapp.action.STOP"
        const val NOTIF_ID = 42
        const val CHANNEL_ID = "track_channel"

        @Volatile var isRecording = false; private set
        val points = CopyOnWriteArrayList<TrackPoint>()
        @Volatile var distanceM = 0.0; private set
        private var lastLoc: Location? = null

        private val iso = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply {
            timeZone = TimeZone.getTimeZone("UTC")
        }

        fun addPoint(loc: Location) {
            lastLoc?.let { distanceM += it.distanceTo(loc) }
            lastLoc = loc
            points.add(TrackPoint(loc.latitude, loc.longitude,
                if (loc.hasAltitude()) loc.altitude else null, iso.format(Date())))
        }

        private fun lastJson(): String {
            val p = points.lastOrNull() ?: return "null"
            val alt = p.alt?.toString() ?: "null"
            return "{\"lat\":${p.lat},\"lon\":${p.lon},\"alt\":$alt,\"time\":\"${p.time}\"}"
        }

        fun statusJson(): String {
            val dist = "%.1f".format(distanceM)
            return "{\"recording\":$isRecording,\"points\":${points.size},\"distanceM\":$dist,\"last\":${lastJson()}}"
        }

        fun stopJson(): String {
            val sb = StringBuilder("{\"ok\":true,\"points\":[")
            points.forEachIndexed { i, p ->
                if (i > 0) sb.append(',')
                val alt = p.alt?.toString() ?: "null"
                sb.append("{\"lat\":${p.lat},\"lon\":${p.lon},\"alt\":$alt,\"time\":\"${p.time}\"}")
            }
            sb.append("]}")
            return sb.toString()
        }

        fun reset() {
            isRecording = false
            points.clear()
            distanceM = 0.0
            lastLoc = null
        }
    }

    private var locationManager: LocationManager? = null
    private var wakeLock: PowerManager.WakeLock? = null
    private var lastNotifUpdate = 0L

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> { start(); return START_STICKY }
            ACTION_STOP -> stop()
        }
        return START_NOT_STICKY
    }

    @SuppressLint("MissingPermission")
    private fun start() {
        if (isRecording) return
        if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_FINE_LOCATION)
            != PackageManager.PERMISSION_GRANTED) { stopSelf(); return }

        points.clear(); distanceM = 0.0; lastLoc = null
        isRecording = true

        // 前台服务 + 通知
        ensureChannel()
        val notif = buildNotification("正在初始化 GPS…")
        if (Build.VERSION.SDK_INT >= 29) {
            startForeground(NOTIF_ID, notif, ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION)
        } else {
            startForeground(NOTIF_ID, notif)
        }

        // 部分唤醒锁（最长 12 小时兜底）
        val pm = getSystemService(POWER_SERVICE) as PowerManager
        wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "lasa:track").apply {
            acquire(12 * 60 * 60 * 1000L)
        }

        locationManager = getSystemService(LOCATION_SERVICE) as LocationManager
        val providers = listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER)
        for (p in providers) {
            try {
                if (locationManager?.isProviderEnabled(p) == true) {
                    locationManager?.requestLocationUpdates(p, 2000L, 3f, this)
                }
            } catch (e: Exception) { /* 忽略单源失败 */ }
        }
        // 立即补一个最近已知位置
        for (p in providers) {
            try {
                locationManager?.getLastKnownLocation(p)?.let { if (points.isEmpty()) addPoint(it) }
            } catch (e: Exception) { /* ignore */ }
        }
    }

    private fun stop() {
        try { locationManager?.removeUpdates(this) } catch (e: Exception) { /* ignore */ }
        try { if (wakeLock?.isHeld == true) wakeLock?.release() } catch (e: Exception) { /* ignore */ }
        isRecording = false
        if (Build.VERSION.SDK_INT >= 24) stopForeground(STOP_FOREGROUND_REMOVE) else @Suppress("DEPRECATION") stopForeground(true)
        stopSelf()
    }

    override fun onDestroy() {
        if (isRecording) stop() else super.onDestroy()
    }

    override fun onLocationChanged(loc: Location) {
        if (!isRecording) return
        // 过滤精度异常点（>80m）
        if (loc.hasAccuracy() && loc.accuracy > 80f && points.size > 1) return
        addPoint(loc)
        // 通知栏每 15 秒最多刷新一次
        val now = System.currentTimeMillis()
        if (now - lastNotifUpdate > 15000) {
            lastNotifUpdate = now
            val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
            nm.notify(NOTIF_ID, buildNotification("已采 ${points.size} 点 · ${"%.2f".format(distanceM / 1000)} km"))
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
    override fun onProviderEnabled(provider: String) {}
    override fun onProviderDisabled(provider: String) {}

    private fun ensureChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
            if (nm.getNotificationChannel(CHANNEL_ID) == null) {
                nm.createNotificationChannel(
                    NotificationChannel(CHANNEL_ID, getString(R.string.track_channel_name), NotificationManager.IMPORTANCE_LOW)
                        .apply { description = getString(R.string.track_channel_desc) }
                )
            }
        }
    }

    private fun buildNotification(text: String): Notification {
        val pi = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val b = if (Build.VERSION.SDK_INT >= 26) Notification.Builder(this, CHANNEL_ID)
        else @Suppress("DEPRECATION") Notification.Builder(this)
        return b.setContentTitle(getString(R.string.track_notif_title))
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setContentIntent(pi)
            .setOngoing(true)
            .build()
    }
}
