# -*- coding: utf-8 -*-
"""部署移动端修复(App.vue/FieldSurvey.vue)到生产 18480：传文件→停后端→限量构建→起后端→reload nginx→验证。"""
import os, paramiko, time

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["frontend/src/App.vue", "frontend/src/views/FieldSurvey.vue"]

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
sftp = c.open_sftp()
for rel in FILES:
    sftp.put(os.path.join(ROOT, rel.replace("/", os.sep)), f"/opt/lasa-nanshan-platform/{rel}")
    log("已上传 " + rel)
sftp.close()

for cmd, to in [
    ("supervisorctl stop lasa-nanshan-backend && echo STOPPED", 60),
    ("cd /opt/lasa-nanshan-platform/frontend && NODE_OPTIONS='--max-old-space-size=512' npx vite build > /tmp/build_field.log 2>&1; echo EXIT=$?; tail -5 /tmp/build_field.log", 280),
    ("supervisorctl start lasa-nanshan-backend && sleep 3 && systemctl reload nginx && echo RELOADED", 90),
    ("curl -s http://127.0.0.1:18480/ | head -c 200; echo; curl -s -o /dev/null -w 'health:%{http_code}\\n' http://127.0.0.1:18481/api/v1/health", 60),
]:
    log("$ " + cmd[:70])
    _, o, e = c.exec_command(cmd, timeout=to)
    log(o.read().decode().strip())
    err = e.read().decode().strip()
    if err: log("STDERR: " + err[:300])
c.close()
log("DEPLOY_DONE")
