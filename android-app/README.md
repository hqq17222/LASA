# 南北山外业调查 Android App（v1.2.0）

配合「拉萨南北山生态监测评估系统」（http://106.15.35.204:18480/）使用的外业调查混合应用。

**分工定位（v1.2.0 起）**：App 只做外业采集四件事——🗺️ 找样地（样地点+共享矢量图层叠加+实时定位导航）、
📷 拍照识别（EXIF 定位 + GLM-4V 识物种）、🌲 样地调查（树高/胸径/郁闭度/盖度）、🥾 轨迹记录；
生态评估、数据展示、气象与物联网监测等全部由网页大系统（电脑端）承担，数据统一落库服务器地理数据库。

## 功能

- **WebView 混合壳**：加载 App 专属移动页 `/m`（`frontend/src/views/MobileField.vue`，地图全屏 + 底部四标签：找样地/拍照识别/样地调查/轨迹），账号体系与平台一致（WebView 内登录一次即可，壳内登录后自动进 `/m`）。
- **原生后台轨迹服务**：网页内点「开始记录（App 后台防熄屏）」→ 启动前台 GPS 服务，熄屏、切后台均持续记录；通知栏实时显示点数与里程。结束后轨迹自动回传网页并同步到平台（外业看板 /ops 可按人查看）。
- **相机/定位限制解除**：HTTP 页面在手机浏览器里被禁用的定位、相机调用，在 App 壳内全部可用。
- **数据安全**：仅放行平台服务器（106.15.35.204）的明文 HTTP，其余流量走系统默认策略。

## 技术结构

```
android-app/
├── settings.gradle / build.gradle / gradle.properties
└── app/
    ├── build.gradle                 # AGP 8.3.2 · Kotlin 1.9.24 · minSdk 24 / targetSdk 34
    └── src/main/
        ├── AndroidManifest.xml      # 权限 + 前台服务（location 类型）+ FileProvider
        ├── java/cn/lasa/fieldapp/
        │   ├── MainActivity.kt      # WebView 壳 + JS 桥(AndroidBridge) + 权限/文件选择
        │   └── TrackService.kt      # 前台轨迹服务（GPS+网络双源、唤醒锁、通知栏）
        └── res/                     # 矢量图标、主题、网络安全配置、FileProvider 路径
```

## 网页 ↔ App 桥接接口（window.AndroidBridge）

| 方法 | 返回（JSON 字符串） | 说明 |
|---|---|---|
| `isApp()` | `true` | 网页检测是否在 App 内运行 |
| `appVersion()` | `"1.2.0"` | App 版本号 |
| `startTrack()` | `{"ok":true}` | 启动原生后台轨迹记录 |
| `stopTrack()` | `{"ok":true,"points":[{lat,lon,alt,time}...]}` | 停止并取回全部轨迹点（UTC ISO 时间） |
| `getStatus()` | `{"recording":bool,"points":n,"distanceM":m,"last":{...}}` | 实时状态轮询 |

平台前端（MobileField.vue / FieldSurvey.vue）已集成：在 App 内自动显示「App 后台模式」记录按钮；在浏览器中则回退到浏览器定位（受 HTTPS 限制时提示导入 GPX）。

## 构建 APK（Android Studio）

1. 安装 **Android Studio**（Koala 2024.1+ 均可，自带 JDK 17 与 Android SDK）。
2. `File → Open` 选择本 `android-app` 目录，等待 Gradle 同步（首次需联网下载依赖）。
3. `Build → Build App Bundle(s) / APK(s) → Build APK(s)`。
4. 产物：`app/build/outputs/apk/debug/app-debug.apk`，拷贝到手机安装即可（首次安装需在系统设置允许「安装未知来源应用」）。

> 若需上架/签名发布：`Build → Generate Signed App Bundle / APK` 创建 keystore 后出 release 包。

## 命令行构建（可选）

```bash
# 需要 JDK 17 + Android SDK（cmdline-tools），并设置 ANDROID_HOME
gradle wrapper          # 首次生成 gradlew
./gradlew assembleDebug # 输出 app-debug.apk
```

## 使用要点（给研究生队员）

1. 安装 APK 后打开，首次启动授予**定位**（建议选「始终允许」或「使用期间允许」）与**通知**权限。
2. 用平台账号登录（如 analyst）。
3. 「科考照片」页拍照/录像 + 注释（物种、树高、胸径、郁闭度等）；照片自动带 GPS 定位并同步媒体库。
4. 「考察轨迹」页用 **App 后台模式** 开始记录；到达样地后熄屏放口袋即可，结束后再同步。
5. 导师/管理员在平台「外业看板」(/ops) 查看：每个队员最后位置、当日里程、样地完成度、共享矢量图层。

## 注意事项

- 轨迹记录期间请勿手动「清理后台」杀掉 App（国产 ROM 建议在系统设置里把本 App 加入自启动/无限制白名单）。
- GPS 精度差（>80m）的漂移点会被自动过滤。
- 轨迹点保存在 App 进程内存中；结束记录并同步后才算落库，长轨迹建议分段保存。
- 若平台域名/IP 变更，需同步修改 `MainActivity.BASE_URL` 与 `network_security_config.xml`。
