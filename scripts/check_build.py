"""服务器端完整构建前端并显示全部输出与退出码。"""
import os
import paramiko

HOST = "106.15.35.204"
PASS = os.environ["LASA_PASS"]

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, 22, "root", PASS, timeout=20)

cmd = (
    "cd /opt/lasa-nanshan-platform/frontend && npx vite build > /tmp/build.log 2>&1; "
    "echo EXIT=$?; tail -30 /tmp/build.log; "
    "find /opt/lasa-nanshan-platform -maxdepth 4 -name 'dist' -o -maxdepth 4 -name 'assets' 2>/dev/null | head"
)
_, o, e = c.exec_command(cmd, timeout=280)
print(o.read().decode()[:4000])
print(e.read().decode()[:400])
c.close()
