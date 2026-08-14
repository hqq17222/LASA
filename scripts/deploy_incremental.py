"""增量部署：上传本次改动文件 → 重启后端(create_all 自动建 field_tracks 表) → 重建前端 → 重载 nginx。"""
import os
import paramiko

HOST = "106.15.35.204"
PASS = os.environ.get("LASA_PASS") or open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE = "/opt/lasa-nanshan-platform"

FILES = [
    "backend/app/models.py",
    "backend/app/schemas.py",
    "backend/app/main.py",
    "backend/app/routers/field_survey.py",
    "frontend/src/api.js",
    "frontend/src/views/FieldSurvey.vue",
]

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, 22, "root", PASS, timeout=20)
sftp = c.open_sftp()
for rel in FILES:
    sftp.put(os.path.join(ROOT, rel.replace("/", os.sep)), f"{REMOTE}/{rel}")
    print("已上传", rel)
sftp.close()

for cmd in [
    "supervisorctl restart lasa-nanshan-backend && sleep 3 && curl -s http://127.0.0.1:18481/api/v1/field/tracks",
    "cd /opt/lasa-nanshan-platform/frontend && npx vite build > /tmp/build2.log 2>&1; echo EXIT=$?; tail -4 /tmp/build2.log",
    "systemctl reload nginx && echo NGINX_OK",
]:
    _, o, e = c.exec_command(cmd, timeout=280)
    print("$", cmd)
    print(o.read().decode()[:2000])
    err = e.read().decode()[:400]
    if err:
        print("STDERR:", err)
c.close()
