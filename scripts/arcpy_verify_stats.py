# -*- coding: utf-8 -*-
"""校验 no000 输出的 NoData，并重试统计值计算。日志写 C:\\tools\\gjob\\job.log。"""
import arcpy, time, sys
from arcpy.sa import Raster

OUT = r"D:\包头湿地\包头DOM\0723第二块-01_no000.tif"
LOG = r"C:\tools\gjob\job.log"

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

try:
    open(LOG, "w").close()
    log("开始校验 + 重试统计值")
    arcpy.CheckOutExtension("Spatial")
    r = Raster(OUT)
    log(f"波段数={r.bandCount} 大小={r.width}x{r.height} NoData值={r.noDataValue}")
    for i in range(1, int(r.bandCount) + 1):
        nd = arcpy.GetRasterProperties_management(OUT + f"\\Band_{i}", "ANYNODATA")
        log(f"  Band_{i} 含NoData: {nd.getOutput(0)}")
    try:
        arcpy.CalculateStatistics_management(OUT)
        log("统计值计算成功")
    except Exception as e:
        log("统计值仍失败(不影响显示与NoData): " + str(e)[:200])
    log("DONE")
except Exception as e:
    log("ERROR: " + str(e))
    sys.exit(1)
