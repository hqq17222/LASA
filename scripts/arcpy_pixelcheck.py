# -*- coding: utf-8 -*-
"""像元级抽查 no000 输出：角部应全为 NoData，中部应为有效像元。日志写 C:\\tools\\gjob\\job.log。"""
import arcpy, time, sys
import numpy as np
from arcpy.sa import Raster

OUT = r"D:\包头湿地\包头DOM\0723第二块-01_no000.tif"
LOG = r"C:\tools\gjob\job.log"

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def sample(r, x0, y0, n, tag):
    arr = arcpy.RasterToNumPyArray(r, arcpy.Point(x0, y0), ncols=n, nrows=n, nodata_to_value=-999)
    if arr.ndim == 2:
        arr = arr[np.newaxis, :, :]
    for i in range(arr.shape[0]):
        b = arr[i]
        tot = b.size
        nd = int((b == -999).sum())
        zero = int((b == 0).sum())
        log(f"  {tag} Band_{i+1}: NoData占比={nd*100.0/tot:.1f}% 零值像元={zero} 最大={b.max()} 最小有效={b[b>0].min() if (b>0).any() else 'NA'}")

try:
    open(LOG, "w").close()
    log("像元级抽查开始")
    arcpy.CheckOutExtension("Spatial")
    r = Raster(OUT)
    cs = r.meanCellWidth
    ex = r.extent
    log(f"像元大小={cs} 范围=({ex.XMin:.2f},{ex.YMin:.2f})-({ex.XMax:.2f},{ex.YMax:.2f}) NoData值={r.noDataValue}")
    n = 300
    log("左下角 300x300:")
    sample(r, ex.XMin, ex.YMin, n, "左下角")
    log("左上角 300x300:")
    sample(r, ex.XMin, ex.YMax - n * cs, n, "左上角")
    log("中心 300x300:")
    sample(r, (ex.XMin + ex.XMax) / 2 - n * cs / 2, (ex.YMin + ex.YMax) / 2 - n * cs / 2, n, "中心")
    log("DONE")
except Exception as e:
    log("ERROR: " + str(e))
    sys.exit(1)
