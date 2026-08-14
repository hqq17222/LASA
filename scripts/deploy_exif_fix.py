"""上传 FieldSurvey.vue（EXIF容错修复）→ 停后端腾内存重建前端 → 恢复。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE = "/opt/lasa-nanshan-platform"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)

sftp = c.open_sftp()
sftp.put(os.path.join(ROOT, "frontend", "src", "views", "FieldSurvey.vue"),
         f"{REMOTE}/frontend/src/views/FieldSurvey.vue")
print("已上传 FieldSurvey.vue")
sftp.close()

CMDS = [
    "supervisorctl stop lasa-nanshan-backend; sleep 2; free -m | head -2",
    "cd /opt/lasa-nanshan-platform/frontend && NODE_OPTIONS='--max-old-space-size=512' npx vite build > /tmp/build_exif.log 2>&1; echo EXIT=$?; tail -8 /tmp/build_exif.log",
    "supervisorctl start lasa-nanshan-backend; sleep 3; systemctl reload nginx; "
    "curl -s -o /dev/null -w 'front:%{http_code} ' http://127.0.0.1:18480/login; "
    "curl -s -o /dev/null -w 'health:%{http_code}' http://127.0.0.1:18481/api/v1/health",
]
for cmd in CMDS:
    _, o, e = c.exec_command(cmd, timeout=280)
    print("$", cmd[:70])
    print(o.read().decode()[:1500])
    err = e.read().decode()[:300]
    if err:
        print("STDERR:", err)
c.close()
