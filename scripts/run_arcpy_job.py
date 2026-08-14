"""后台启动 arcpy 作业并立即返回（长任务轮询日志）。"""
import os, subprocess, sys

os.makedirs(r"C:\tools\gjob", exist_ok=True)
ARCPY = r"D:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
JOB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   sys.argv[1] if len(sys.argv) > 1 else "arcpy_remove_000.py")
logf = open(r"C:\tools\gjob\job_stdout.log", "w", encoding="utf-8")
p = subprocess.Popen([ARCPY, JOB], stdout=logf, stderr=subprocess.STDOUT,
                     creationflags=subprocess.CREATE_NO_WINDOW)
print("已启动 arcpy 作业，PID =", p.pid)
