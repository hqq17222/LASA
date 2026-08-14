# -*- coding: utf-8 -*-
"""arcpy 作业：将 0723第二块-01.tif 中 RGB 全为 0 的像元置为 NoData。
原文件不动，输出 0723第二块-01_no000.tif。日志写 C:\\tools\\gjob\\job.log。"""
import arcpy, os, time, sys
from arcpy.sa import Raster, SetNull

IN = r"D:\包头湿地\包头DOM\0723第二块-01.tif"
OUT = r"D:\包头湿地\包头DOM\0723第二块-01_no000.tif"
LOG = r"C:\tools\gjob\job.log"

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

try:
    open(LOG, "w").close()
    log("启动 arcpy 作业")
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.overwriteOutput = True
    arcpy.env.compression = "LZW"
    arcpy.env.pyramid = "NONE"

    rin = Raster(IN)
    log(f"输入: bands={rin.bandCount} size={rin.width}x{rin.height}")
    if os.path.exists(OUT):
        arcpy.Delete_management(OUT); log("已删除旧输出")

    log("构建掩膜 (Band1==0)&(Band2==0)&(Band3==0) ...")
    mask = (Raster(IN + "\\Band_1") == 0) & (Raster(IN + "\\Band_2") == 0) & (Raster(IN + "\\Band_3") == 0)

    log("逐波段 SetNull 计算 ...")
    b1 = SetNull(mask, Raster(IN + "\\Band_1"))
    b2 = SetNull(mask, Raster(IN + "\\Band_2"))
    b3 = SetNull(mask, Raster(IN + "\\Band_3"))

    log("合成波段并写出栅格 ...")
    arcpy.CompositeBands_management([b1, b2, b3], OUT)
    log(f"已保存: {OUT} ({os.path.getsize(OUT)/1e9:.2f} GB)")

    log("构建金字塔 ...")
    arcpy.BuildPyramids_management(OUT)
    log("计算统计值 ...")
    arcpy.CalculateStatistics_management(OUT)

    # 验证：输出波段与 NoData（校验失败不影响主体成果）
    try:
        r2 = Raster(OUT)
        log(f"输出校验: bands={r2.bandCount}")
        for i in range(1, int(r2.bandCount) + 1):
            nd = arcpy.GetRasterProperties_management(OUT + f"\\Band_{i}", "ANYNODATA")
            log(f"  Band_{i} 含NoData: {nd.getOutput(0)}")
    except Exception as e2:
        log("校验段异常(主体已完成): " + str(e2))
    log("DONE")
except Exception as e:
    log("ERROR: " + str(e))
    sys.exit(1)
