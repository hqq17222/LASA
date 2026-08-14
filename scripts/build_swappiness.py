"""swappiness 调为 60（持久化），停后端重建前端，恢复。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
for cmd in [
    "sysctl -w vm.swappiness=60 && (grep -q vm.swappiness /etc/sysctl.conf && sed -i 's/^vm.swappiness.*/vm.swappiness=60/' /etc/sysctl.conf || echo 'vm.swappiness=60' >> /etc/sysctl.conf) && tail -1 /etc/sysctl.conf",
    "supervisorctl stop lasa-nanshan-backend; sleep 2; free -m | head -3",
    "cd /opt/lasa-nanshan-platform/frontend && NODE_OPTIONS='--max-old-space-size=512' npx vite build > /tmp/build_sw.log 2>&1; echo EXIT=$?; tail -4 /tmp/build_sw.log",
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
