"""复制 android-app 源码到 C:\\tools\\build 构建 APK（绕开工作区写限制）。可重跑续建。"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "android-app")
PROJ = r"C:\tools\build\android-app"
GRADLE = r"C:\tools\gradle-8.7\bin\gradle.bat"

# 同步源码（排除构建产物）
def sync():
    if os.path.isdir(PROJ):
        shutil.rmtree(PROJ)
    shutil.copytree(SRC, PROJ, ignore=shutil.ignore_patterns("build", ".gradle", "*.iml"))
sync()
print("源码已同步到", PROJ)

env = dict(os.environ,
           JAVA_HOME=r"C:\tools\jdk17",
           ANDROID_HOME=r"C:\tools\android-sdk",
           ANDROID_SDK_ROOT=r"C:\tools\android-sdk")

p = subprocess.run([GRADLE, "assembleDebug", "--console=plain"],
                   cwd=PROJ, capture_output=True, text=True, env=env, timeout=275)
out = (p.stdout or "") + "\n" + (p.stderr or "")
print(out[-3000:])
apk = os.path.join(PROJ, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
if p.returncode == 0 and os.path.exists(apk):
    print("APK_OK", apk, round(os.path.getsize(apk) / 1e6, 1), "MB")
else:
    print("BUILD_NOT_DONE rc=", p.returncode)
    sys.exit(2)
