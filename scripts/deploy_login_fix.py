"""上传登录容错修复（Login.vue + auth.py）-> 重启后端 -> 重建前端 -> 恢复。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE = "/opt/lasa-nanshan-platform"

FILES = [
    "backend/app/routers/auth.py",
    "frontend/src/views/Login.vue",
]

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)

sftp = c.open_sftp()
for rel in FILES:
    sftp.put(os.path.join(ROOT, rel.replace("/", os.sep)), f"{REMOTE}/{rel}")
    print("已上传", rel)
sftp.close()

CMDS = [
    "supervisorctl stop lasa-nanshan-backend; sleep 2; "
    "cd /opt/lasa-nanshan-platform/frontend && NODE_OPTIONS='--max-old-space-size=512' npx vite build > /tmp/build_login.log 2>&1; echo EXIT=$?; tail -4 /tmp/build_login.log",
    "supervisorctl start lasa-nanshan-backend; sleep 3; systemctl reload nginx; "
    "curl -s -o /dev/null -w 'front:%{http_code} ' http://127.0.0.1:18480/login; "
    "curl -s -X POST http://127.0.0.1:18481/api/v1/auth/login -H 'Content-Type: application/json' "
    "-d '{\"username\":\" admin \",\"password\":\" 30010223 \"}' -o /dev/null -w 'trim-login:%{http_code}'",
]
for cmd in CMDS:
    _, o, e = c.exec_command(cmd, timeout=280)
    print("$", cmd[:70])
    print(o.read().decode()[:1200])
    err = e.read().decode()[:300]
    if err:
        print("STDERR:", err)
c.close()
