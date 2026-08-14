"""给服务器添加 2G swap 并重新构建前端。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)

CMDS = [
    "swapon --show; [ -f /swapfile ] && echo SWAP_EXISTS || (fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile && echo '/swapfile none swap sw 0 0' >> /etc/fstab && echo SWAP_ADDED)",
    "free -m | head -3",
    "cd /opt/lasa-nanshan-platform/frontend && npx vite build > /tmp/build_swap.log 2>&1; echo EXIT=$?; tail -6 /tmp/build_swap.log",
    "systemctl reload nginx && curl -s -o /dev/null -w 'front:%{http_code}' http://127.0.0.1:18480/login",
]
for cmd in CMDS:
    _, o, e = c.exec_command(cmd, timeout=280)
    print("$", cmd[:70])
    print(o.read().decode()[:1500])
    err = e.read().decode()[:300]
    if err:
        print("STDERR:", err)
c.close()
