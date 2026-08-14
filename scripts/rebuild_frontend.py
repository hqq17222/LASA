"""上传修复后的前端文件并在服务器端重新构建、重载 nginx。"""
import os
import paramiko

HOST = "106.15.35.204"
PASS = os.environ["LASA_PASS"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = [
    ("frontend/src/views/Alarms.vue", "/opt/lasa-nanshan-platform/frontend/src/views/Alarms.vue"),
]

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, 22, "root", PASS, timeout=20)
sftp = c.open_sftp()
for local, remote in FILES:
    sftp.put(os.path.join(ROOT, local.replace("/", os.sep)), remote)
    print("已上传", local)
sftp.close()

for cmd in [
    "cd /opt/lasa-nanshan-platform/frontend && npx vite build 2>&1 | tail -8",
    "ls -la /opt/lasa-nanshan-platform/frontend/dist | head -6",
    "systemctl reload nginx && curl -s -o /dev/null -w 'HTTP:%{http_code}' http://127.0.0.1:18480/",
]:
    _, o, e = c.exec_command(cmd, timeout=240)
    print("$", cmd)
    print(o.read().decode()[:1500])
    err = e.read().decode()[:400]
    if err:
        print("STDERR:", err)
c.close()
