# 拉萨南北山绿化监测平台（LASA）

西藏拉萨南北山绿化工程生态监测与外业调查一体化系统。

## 系统组成

| 目录 | 说明 |
|---|---|
| `backend/` | FastAPI 后端：用户权限、生态评估指标、地图图层、外业照片（EXIF 自动解析定位）、轨迹、样地、外业看板等 API |
| `frontend/` | Vue 3 + Vite + Leaflet 前端：监测大屏、生态评估、地图、巡检照片、用户管理、使用说明等 |
| `android-app/` | 安卓外业 App（Kotlin）：WebView 壳 + 前台轨迹记录服务 + JS 桥，配合平台做样地调查、拍照上传、轨迹记录 |
| `scripts/` | 运维与部署脚本（SSH 部署、前端构建、APK 构建、ArcPy 栅格处理等） |

## 线上部署

- 地址：http://106.15.35.204:18480/
- 阿里云服务器：nginx（反向代理）+ supervisor（托管后端 uvicorn）
- 配置文件：`scripts/lasa-nanshan-platform.nginx.conf`、`scripts/lasa-nanshan-platform.supervisor.ini`
- 服务器内存较小（构建前端易 OOM）：先 `supervisorctl stop` 后端腾出内存，`NODE_OPTIONS='--max-old-space-size=512' npx vite build`，再 start + nginx reload；swappiness 已调 60 并加了 2G swap

## 用户等级

四级用户组：管理员 admin、管理 manager、分析 analyst、查看 viewer（前端 `views/Users.vue` 管理）。

## 本地开发

```bash
# 后端
cd backend && pip install -r requirements.txt && bash start.sh
# 前端
cd frontend && npm install && npm run dev
```

## App 构建

`scripts/build_apk.py`：把 `android-app` 同步到构建目录后用 Gradle 出 debug 包
（构建机需 JDK17 + Android SDK platform-34/build-tools 34.0.0 + Gradle 8.7）。
构建产物 APK 由 `scripts/upload_apk.py` 上传到平台 `/static/` 供下载。

## 保密注意

- `scripts/.lasa_pass`（服务器 SSH 密码）**不在本仓库**，需要时向黄老师索取。
- 部分运维脚本中含平台 admin 密码明文，仓库已设为私有，请勿外传或转为公开。
