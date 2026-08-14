"""服务器端限内存重新构建前端。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
cmd = (
    "free -m | head -2; cd /opt/lasa-nanshan-platform/frontend && "
    "NODE_OPTIONS=--max-old-space-size=768 npx vite build > /tmp/build3.log 2>&1; "
    "echo EXIT=$?; tail -5 /tmp/build3.log; ls dist 2>/dev/null"
)
_, o, e = c.exec_command(cmd, timeout=280)
print(o.read().decode()[:2000])
print(e.read().decode()[:300])
c.close()
