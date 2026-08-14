"""修改管理员密码并验证新密码可登录。"""
import json
import os
import urllib.request
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
NEW_PW = "30010223"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
cmd = (
    "cd /opt/lasa-nanshan-platform/backend && venv/bin/python -c \""
    "from app.core.database import SessionLocal\n"
    "from app.core import security as sec\n"
    "from app.models import User, AuthToken\n"
    "db = SessionLocal()\n"
    "u = db.query(User).filter(User.username=='admin').first()\n"
    "u.password_hash = sec.hash_password('" + NEW_PW + "')\n"
    "db.query(AuthToken).filter(AuthToken.user_id==u.id).delete()\n"
    "db.commit()\n"
    "print('PW_UPDATED')\n"
    "\""
)
_, o, e = c.exec_command(cmd, timeout=60)
print(o.read().decode(), e.read().decode()[:300])
c.close()

# 验证：旧密码应失败，新密码应成功
def login(pw):
    req = urllib.request.Request(
        "http://106.15.35.204:18480/api/v1/auth/login",
        data=json.dumps({"username": "admin", "password": pw}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as ex:
        return ex.code

import urllib.error
print("旧密码登录(应401):", login("Lasa@2026"))
print("新密码登录(应200):", login(NEW_PW))
