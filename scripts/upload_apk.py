"""上传 APK 到服务器静态目录并验证下载链接；同时尝试复制到工作区。"""
import os, shutil, sys, paramiko

APK = r"C:\tools\build\android-app\app\build\outputs\apk\debug\app-debug.apk"
NAME = sys.argv[1] if len(sys.argv) > 1 else "lasa-field-app-v1.0.0.apk"
PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1) 复制到工作区（可能受沙箱限制，失败则跳过）
try:
    dst = os.path.join(ROOT, "android-app", NAME)
    shutil.copy(APK, dst)
    print("工作区副本:", dst)
except Exception as e:
    print("工作区复制跳过：", e)

# 2) 上传服务器
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
sftp = c.open_sftp()
remote = f"/opt/lasa-nanshan-platform/backend/data/uploads/{NAME}"
sftp.put(APK, remote)
print("已上传", remote)
sftp.close()
_, o, e = c.exec_command(
    f"curl -s -o /dev/null -w 'download:%{{http_code}} %{{size_download}}bytes\\n' http://127.0.0.1:18480/static/{NAME}",
    timeout=60)
print(o.read().decode())
c.close()
