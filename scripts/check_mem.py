"""检查服务器内存占用进程，清理残留 node 进程后重建前端。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
for cmd in [
    "ps aux --sort=-rss | head -12",
    "pkill -9 -f 'vite' ; pkill -9 -f 'esbuild'; pkill -9 -f 'node .*build'; sleep 1; free -m | head -2",
]:
    _, o, e = c.exec_command(cmd, timeout=60)
    print("$", cmd[:50])
    print(o.read().decode()[:1500])
    err = e.read().decode()[:200]
    if err:
        print("STDERR:", err)
c.close()
