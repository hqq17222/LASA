# -*- coding: utf-8 -*-
"""端到端验证:登录 -> 上传一张带GPS EXIF的测试照片 -> 检查后端是否解析出坐标。"""
import io, json, requests
from PIL import Image
from PIL.TiffImagePlugin import IFDRational

BASE = "http://106.15.35.204:18480"

r = requests.post(f"{BASE}/api/v1/auth/login",
                  json={"username": "admin", "password": "30010223"}, timeout=30)
assert r.status_code == 200, r.text
token = r.json().get("access_token") or r.json()["token"]
print("登录 OK")

def make_test_jpeg():
    img = Image.new("RGB", (800, 600), (76, 175, 80))
    exif = Image.Exif()
    exif[0x0110] = "TestCam X1"      # Model
    exif[0x0132] = "2026:08:05 17:30:00"  # DateTime
    R = lambda n, d=1: IFDRational(n, d)
    gps = {
        0: (2, 3, 0, 0),             # GPSVersionID
        1: "N", 2: (R(29), R(39), R(72, 10)),   # 29°39'7.2"N
        3: "E", 4: (R(91), R(10), R(192, 10)),  # 91°10'19.2"E
        6: R(3658),                  # altitude m
    }
    exif[0x8825] = gps
    buf = io.BytesIO()
    img.save(buf, "JPEG", exif=exif.tobytes())
    buf.seek(0)
    return buf

buf = make_test_jpeg()
r = requests.post(f"{BASE}/api/v1/patrol-photos/upload",
                  data={"project_id": 1, "note": "EXIF自测照片"},
                  files={"file": ("gps_test.jpg", buf, "image/jpeg")},
                  headers={"Authorization": f"Bearer {token}"}, timeout=120)
print("上传:", r.status_code)
d = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
if r.status_code != 200:
    print("错误:", r.text[:500]); raise SystemExit(1)
print(json.dumps({k: d.get(k) for k in ("id", "lon", "lat", "altitude", "shoot_time")},
                 ensure_ascii=False))
with open("test_photo_id.txt", "w") as f:
    f.write(str(d.get("id", "")))
if d.get("lon") and abs(d["lon"] - 91.172) < 0.001:
    print("OK 后端 EXIF 解析正常")
else:
    print("FAIL 后端未解析出 GPS")
