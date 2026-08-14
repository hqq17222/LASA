"""服务器端排查并修复：查找 dist、必要时重新构建前端、校验 nginx 配置。"""
import os
import paramiko

HOST = "106.15.35.204"
PASS = os.environ["LASA_PASS"]

CMDS = [
    "find /opt/lasa-nanshan-platform -maxdepth 3 -name dist 2>/dev/null; "
    "find /opt/lasa-nanshan-platform -maxdepth 3 -name index.html 2>/dev/null | head",
    "grep -n 'root\\|try_files\\|index' /etc/nginx/conf.d/lasa-nanshan-platform.conf",
    "cd /opt/lasa-nanshan-platform/frontend && npx vite build 2>&1 | tail -12 && ls -la dist | head -8",
    "nginx -t 2>&1 && systemctl reload nginx && echo RELOADED",
]

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, 22, "root", PASS, timeout=20)
for cmd in CMDS:
    _, o, e = c.exec_command(cmd, timeout=180)
    print("$", cmd)
    print(o.read().decode()[:2500])
    err = e.read().decode()[:500]
    if err:
        print("STDERR:", err)
c.close()
