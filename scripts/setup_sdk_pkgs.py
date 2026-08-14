"""接受 SDK 许可 + 安装 platform-tools / platforms;android-34 / build-tools;34.0.0。"""
import os, subprocess, sys

SDK = r"C:\tools\android-sdk"
MGR = os.path.join(SDK, "cmdline-tools", "latest", "bin", "sdkmanager.bat")
env = dict(os.environ, JAVA_HOME=r"C:\tools\jdk17")

# 1) 接受许可（自动回 y）
p = subprocess.run(MGR + " --licenses", input="y\n" * 60, capture_output=True, text=True, env=env, timeout=240, shell=True)
print("licenses rc=", p.returncode, (p.stdout or "")[-200:])

# 2) 安装组件（可重跑续装）
pkgs = "platform-tools platforms;android-34 build-tools;34.0.0"
p = subprocess.run(f'"{MGR}" {pkgs}', capture_output=True, text=True, env=env, timeout=270, shell=True)
print("install rc=", p.returncode)
print((p.stdout or "")[-800:])
if p.returncode != 0:
    print("STDERR:", (p.stderr or "")[-400:])
    sys.exit(2)
for d in ["platform-tools", os.path.join("platforms", "android-34"), os.path.join("build-tools", "34.0.0")]:
    print(d, "OK" if os.path.isdir(os.path.join(SDK, d)) else "MISSING")
