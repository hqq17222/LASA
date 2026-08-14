"""本地构建前端（绕开服务器 OOM），成功后上传 dist 到服务器并重载 nginx。"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONT = os.path.join(ROOT, "frontend")
NPM = r"C:\Users\huang\AppData\Roaming\kimi-desktop\daimon-share\daimon\command-process-owner\bin\npm.cmd"

def run(args, timeout):
    print("$", " ".join(args))
    p = subprocess.run(args, cwd=FRONT, capture_output=True, text=True, timeout=timeout, shell=True)
    print((p.stdout or "")[-1500:])
    if p.returncode != 0:
        print("STDERR:", (p.stderr or "")[-800:])
        sys.exit(1)

if not os.path.isdir(os.path.join(FRONT, "node_modules")):
    run([NPM, "install", "--no-audit", "--no-fund"], 280)
else:
    print("node_modules 已存在，跳过安装")
run([NPM, "run", "build"], 280)
