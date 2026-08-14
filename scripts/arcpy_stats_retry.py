# -*- coding: utf-8 -*-
"""重试统计值(跳行采样)并检查金字塔文件。日志写 C:\\tools\\gjob\\job.log。"""
import arcpy, os, time, sys

OUT = r"D:\包头湿地\包头DOM\0723第二块-01_no000.tif"
LOG = r"C:\tools\gjob\job.log"

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

try:
    open(LOG, "w").close()
    log("检查金字塔 + 重试统计值")
    ovr = OUT + ".ovr"
    log(f"ovr存在: {os.path.exists(ovr)}")
    if not os.path.exists(ovr):
        try:
            arcpy.BuildPyramids_management(OUT)
            log(f"重建金字塔后 ovr存在: {os.path.exists(ovr)}")
        except Exception as e:
            log("金字塔重建失败: " + str(e)[:150])
    try:
        arcpy.CalculateStatistics_management(OUT, 10, 10)
        log("统计值计算成功(跳行x10)")
    except Exception as e:
        log("统计值仍失败(不影响使用,Pro加载时会即时统计): " + str(e)[:150])
    log("DONE")
except Exception as e:
    log("ERROR: " + str(e))
    sys.exit(1)
