"""部署用户管理模块：上传改动文件 → 重启后端自动建表 → 播种管理员 → 重建前端(失败重试) → 重载 nginx。"""
import os
import paramiko

HOST = "106.15.35.204"
PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE = "/opt/lasa-nanshan-platform"

FILES = [
    "backend/app/models.py",
    "backend/app/schemas.py",
    "backend/app/main.py",
    "backend/app/core/security.py",
    "backend/app/routers/auth.py",
    "backend/app/routers/users.py",
    "frontend/src/api.js",
    "frontend/src/router.js",
    "frontend/src/App.vue",
    "frontend/src/components/Layout.vue",
    "frontend/src/views/Login.vue",
    "frontend/src/views/Users.vue",
    "frontend/src/views/PatrolPhotos.vue",
    "frontend/src/views/FieldSurvey.vue",
]

SEED_ADMIN = (
    "cd /opt/lasa-nanshan-platform/backend && venv/bin/python -c \""
    "from app.core.database import SessionLocal, init_db\n"
    "from app.core import security as sec\n"
    "from app.models import User\n"
    "init_db()\n"
    "db = SessionLocal()\n"
    "n = db.query(User).count()\n"
    "if n == 0:\n"
    "    db.add(User(username='admin', password_hash=sec.hash_password('Lasa@2026'), display_name='系统管理员', role='admin'))\n"
    "    db.commit(); print('ADMIN_SEEDED')\n"
    "else:\n"
    "    print('USERS_EXIST', n)\n"
    "\""
)

def run(c, cmd, timeout=280):
    _, o, e = c.exec_command(cmd, timeout=timeout)
    out = o.read().decode()[:1800]
    err = e.read().decode()[:300]
    print("$", cmd[:80])
    print(out)
    if err:
        print("STDERR:", err)
    return out

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, 22, "root", PASS, timeout=20)
sftp = c.open_sftp()
for rel in FILES:
    sftp.put(os.path.join(ROOT, rel.replace("/", os.sep)), f"{REMOTE}/{rel}")
    print("已上传", rel)
sftp.close()

run(c, "supervisorctl restart lasa-nanshan-backend && sleep 3 && curl -s -o /dev/null -w 'health:%{http_code}' http://127.0.0.1:18481/api/v1/health && echo && curl -s -o /dev/null -w 'projects-noauth:%{http_code}' http://127.0.0.1:18481/api/v1/projects")
run(c, SEED_ADMIN)
out = run(c, "cd /opt/lasa-nanshan-platform/frontend && npx vite build > /tmp/build_auth.log 2>&1; echo EXIT=$?; tail -3 /tmp/build_auth.log")
if "EXIT=0" not in out:
    print("首次构建失败，重试一次...")
    run(c, "sleep 5; cd /opt/lasa-nanshan-platform/frontend && npx vite build > /tmp/build_auth2.log 2>&1; echo EXIT=$?; tail -3 /tmp/build_auth2.log")
run(c, "systemctl reload nginx && curl -s -o /dev/null -w 'front:%{http_code}' http://127.0.0.1:18480/login")
c.close()
print("部署完成")
