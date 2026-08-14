# -*- coding: utf-8 -*-
"""备份前侦察：服务器目录结构、数据库文件、上传目录体积。"""
import os, paramiko

HOST = "106.15.35.204"
PASS = os.environ.get("LASA_PASS") or open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, 22, "root", PASS, timeout=20)
for cmd in [
    "ls /opt/lasa-nanshan-platform/",
    "du -sh /opt/lasa-nanshan-platform/* 2>/dev/null | sort -rh | head -15",
    "find /opt/lasa-nanshan-platform/backend -maxdepth 2 -name '*.db' -o -maxdepth 2 -name '*.sqlite*' 2>/dev/null | head",
    "ls /opt/lasa-nanshan-platform/backend/ | head -20",
    "find /opt/lasa-nanshan-platform -maxdepth 3 -type d -name '*upload*' -o -maxdepth 3 -type d -name '*media*' -o -maxdepth 3 -type d -name 'static' 2>/dev/null | head",
    "which sqlite3; python3 -c 'import sqlite3; print(\"sqlite3 module ok\", sqlite3.sqlite_version)'",
    "df -h /opt | tail -1",
    "free -m | head -2",
]:
    _, o, e = c.exec_command(cmd, timeout=60)
    print("$", cmd)
    print(o.read().decode().strip())
    err = e.read().decode().strip()
    if err: print("STDERR:", err[:200])
c.close()
