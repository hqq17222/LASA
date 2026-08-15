# -*- coding: utf-8 -*-
"""本地构建的前端 dist 上传到生产服务器并热替换（不动后端，零停机）。"""
import os, tarfile, time, paramiko

DIST = r"C:\tools\build\frontend\dist"
PKG = r"C:\tools\gjob\dist_field_fix.tar.gz"
PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

# 本地校验新代码在包里
js = [f for f in os.listdir(os.path.join(DIST, "assets")) if f.endswith(".js")][0]
code = open(os.path.join(DIST, "assets", js), encoding="utf-8").read()
for kw in ["南北山外业", "找样地", "identify", "surveys"]:
    log(f"包内校验 '{kw}': {kw in code}")

with tarfile.open(PKG, "w:gz") as t:
    t.add(DIST, arcname="dist")
log(f"打包完成 {os.path.getsize(PKG)/1e6:.1f} MB")

c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
sftp = c.open_sftp()
sftp.put(PKG, "/tmp/dist_field_fix.tar.gz")
sftp.close()
log("已上传服务器")

TS = time.strftime("%Y%m%d%H%M%S")
for cmd in [
    f"cd /opt/lasa-nanshan-platform/frontend && mv dist dist.bak.{TS} && tar xzf /tmp/dist_field_fix.tar.gz && echo REPLACED",
    "grep -o 'assets/index-[^\"]*\\.js' /opt/lasa-nanshan-platform/frontend/dist/index.html",
    "curl -s -o /dev/null -w 'site:%{http_code}\\n' http://127.0.0.1:18480/",
    "curl -s -o /dev/null -w 'api:%{http_code}\\n' http://127.0.0.1:18481/api/v1/health",
]:
    _, o, e = c.exec_command(cmd, timeout=120)
    log("$ " + cmd[:60] + " → " + o.read().decode().strip())
    err = e.read().decode().strip()
    if err: log("STDERR: " + err[:200])
c.close()
log("DIST_DONE")
