"""部署外业看板+App配套web改动：上传 -> 后端重启(迁移新表新列) -> 重建前端 -> 恢复 -> 接口验证。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE = "/opt/lasa-nanshan-platform"

FILES = [
    "backend/app/models.py",
    "backend/app/core/database.py",
    "backend/app/schemas.py",
    "backend/app/routers/field_survey.py",
    "backend/app/routers/patrol_photos.py",
    "frontend/index.html",
    "frontend/src/api.js",
    "frontend/src/router.js",
    "frontend/src/components/Layout.vue",
    "frontend/src/views/OpsBoard.vue",
    "frontend/src/views/PatrolPhotos.vue",
    "frontend/src/views/FieldSurvey.vue",
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
    "supervisorctl restart lasa-nanshan-backend && sleep 4 && curl -s http://127.0.0.1:18481/api/v1/health",
    "supervisorctl stop lasa-nanshan-backend; sleep 2; "
    "cd /opt/lasa-nanshan-platform/frontend && NODE_OPTIONS='--max-old-space-size=512' npx vite build > /tmp/build_ops.log 2>&1; echo EXIT=$?; tail -4 /tmp/build_ops.log",
    "supervisorctl start lasa-nanshan-backend; sleep 3; systemctl reload nginx; "
    "curl -s -o /dev/null -w 'front:%{http_code} ' http://127.0.0.1:18480/login; "
    "curl -s -o /dev/null -w 'health:%{http_code}' http://127.0.0.1:18481/api/v1/health",
]
for cmd in CMDS:
    _, o, e = c.exec_command(cmd, timeout=280)
    print("$", cmd[:70])
    print(o.read().decode()[:1200])
    err = e.read().decode()[:300]
    if err:
        print("STDERR:", err)
c.close()
