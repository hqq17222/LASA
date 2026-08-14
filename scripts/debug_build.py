"""排查构建被杀原因并检查 dist 现状。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
for cmd in [
    "dmesg -T 2>/dev/null | tail -8 || journalctl -k --no-pager | tail -8",
    "ls -la --time-style=+%H:%M /opt/lasa-nanshan-platform/frontend/dist /opt/lasa-nanshan-platform/frontend/dist/assets 2>/dev/null; date +%H:%M",
    "grep -o 'index-[^\"]*\\.js' /opt/lasa-nanshan-platform/frontend/dist/index.html 2>/dev/null",
    "ulimit -a | grep -i 'virtual\\|processes\\|memory'",
]:
    _, o, e = c.exec_command(cmd, timeout=60)
    print("$", cmd[:60])
    print(o.read().decode()[:1500])
    err = e.read().decode()[:300]
    if err:
        print("STDERR:", err)
c.close()
