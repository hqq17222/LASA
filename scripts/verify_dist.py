"""校验服务器 dist 是否为新构建且包含轨迹同步代码，并重载 nginx。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
for cmd in [
    "ls -la --time-style=+%H:%M /opt/lasa-nanshan-platform/frontend/dist /opt/lasa-nanshan-platform/frontend/dist/assets && date +%H:%M",
    "grep -l 'field/tracks' /opt/lasa-nanshan-platform/frontend/dist/assets/*.js && echo SYNC_CODE_OK",
    "grep -o 'index-[^\"]*\\.js' /opt/lasa-nanshan-platform/frontend/dist/index.html",
    "systemctl reload nginx && curl -s -o /dev/null -w 'HTTP:%{http_code}\\n' http://127.0.0.1:18480/ && curl -s http://127.0.0.1:18480/api/v1/field/tracks",
]:
    _, o, e = c.exec_command(cmd, timeout=60)
    print("$", cmd[:60])
    print(o.read().decode()[:1200])
    err = e.read().decode()[:300]
    if err:
        print("STDERR:", err)
c.close()
