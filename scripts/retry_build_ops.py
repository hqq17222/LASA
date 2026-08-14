"""确认 swap 状态，降堆上限重建前端。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
for cmd in [
    "free -m; swapon --show",
    "swapon /swapfile2 2>/dev/null; supervisorctl stop lasa-nanshan-backend; sleep 2; sync; echo 3 > /proc/sys/vm/drop_caches; free -m | head -2",
    "cd /opt/lasa-nanshan-platform/frontend && NODE_OPTIONS='--max-old-space-size=448 --max-semi-space-size=8' npx vite build > /tmp/build_ops2.log 2>&1; echo EXIT=$?; tail -4 /tmp/build_ops2.log",
    "supervisorctl start lasa-nanshan-backend; sleep 3; systemctl reload nginx; "
    "curl -s -o /dev/null -w 'front:%{http_code} ' http://127.0.0.1:18480/login; "
    "curl -s -o /dev/null -w 'health:%{http_code}' http://127.0.0.1:18481/api/v1/health",
]:
    _, o, e = c.exec_command(cmd, timeout=280)
    print("$", cmd[:60])
    print(o.read().decode()[:1200])
    err = e.read().decode()[:300]
    if err:
        print("STDERR:", err)
c.close()
