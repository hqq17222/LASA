"""swapfile2 写入 fstab 持久化；最终验证登录与页面。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
for cmd in [
    "grep -q '/swapfile2' /etc/fstab || echo '/swapfile2 none swap sw 0 0' >> /etc/fstab; tail -2 /etc/fstab",
    "curl -s -X POST http://127.0.0.1:18481/api/v1/auth/login -H 'Content-Type: application/json' "
    "-d '{\"username\":\" admin \",\"password\":\" 30010223 \"}' -o /dev/null -w 'trim-login:%{http_code}\\n'",
    "curl -s -o /dev/null -w 'public-front:%{http_code}\\n' http://127.0.0.1:18480/",
]:
    _, o, e = c.exec_command(cmd, timeout=60)
    print("$", cmd[:60])
    print(o.read().decode()[:600])
    err = e.read().decode()[:200]
    if err:
        print("STDERR:", err)
c.close()
