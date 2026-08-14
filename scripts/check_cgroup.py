"""查 cgroup 内存上限与 swappiness，据此决定策略。"""
import os
import paramiko

PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("106.15.35.204", 22, "root", PASS, timeout=20)
for cmd in [
    "cat /sys/fs/cgroup/memory.max 2>/dev/null; cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null; echo ---; cat /proc/sys/vm/swappiness",
    "systemctl show --property=MemoryMax,MemoryHigh,MemoryLimit $(systemctl status lasa-nanshan-backend --no-pager -l 2>/dev/null | grep -o '[^ ]*\\.slice' | head -1) 2>/dev/null | head -5; cat /proc/self/cgroup",
]:
    _, o, e = c.exec_command(cmd, timeout=60)
    print("$", cmd[:60])
    print(o.read().decode()[:800])
    err = e.read().decode()[:200]
    if err:
        print("STDERR:", err)
c.close()
