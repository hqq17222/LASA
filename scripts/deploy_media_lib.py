"""部署媒体库+补标功能：上传改动文件 -> 重启后端(自动迁移新列) -> 停后端重建前端 -> 恢复。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE = "/opt/lasa-nanshan-platform"

FILES = [
    "backend/app/models.py",
    "backend/app/core/database.py",
    "backend/app/routers/patrol_photos.py",
    "frontend/src/api.js",
    "frontend/src/views/FieldSurvey.vue",
    "frontend/src/views/PatrolPhotos.vue",
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
    # 先重启后端让迁移生效并验证接口
    "supervisorctl restart lasa-nanshan-backend && sleep 4 && curl -s http://127.0.0.1:18481/api/v1/health",
    # 停后端腾内存重建前端
    "supervisorctl stop lasa-nanshan-backend; sleep 2; "
    "cd /opt/lasa-nanshan-platform/frontend && NODE_OPTIONS='--max-old-space-size=512' npx vite build > /tmp/build_media.log 2>&1; echo EXIT=$?; tail -6 /tmp/build_media.log",
    # 恢复
    "supervisorctl start lasa-nanshan-backend; sleep 3; systemctl reload nginx; "
    "curl -s -o /dev/null -w 'front:%{http_code} ' http://127.0.0.1:18480/login; "
    "curl -s -o /dev/null -w 'health:%{http_code}' http://127.0.0.1:18481/api/v1/health",
]
for cmd in CMDS:
    _, o, e = c.exec_command(cmd, timeout=280)
    print("$", cmd[:80])
    print(o.read().decode()[:1500])
    err = e.read().decode()[:300]
    if err:
        print("STDERR:", err)
c.close()
