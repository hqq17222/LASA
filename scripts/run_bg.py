# -*- coding: utf-8 -*-
"""后台启动任意 python 脚本（托管解释器），日志写 C:\\tools\\gjob\\bg_<名字>.log。"""
import os, subprocess, sys

os.makedirs(r"C:\tools\gjob", exist_ok=True)
job = sys.argv[1]
logf = open(rf"C:\tools\gjob\bg_{os.path.basename(job)}.log", "w", encoding="utf-8")
p = subprocess.Popen([sys.executable, job] + sys.argv[2:], stdout=logf, stderr=subprocess.STDOUT,
                     creationflags=subprocess.CREATE_NO_WINDOW)
print("已启动, PID =", p.pid, "| 日志:", logf.name)
