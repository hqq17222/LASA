"""外网验证轨迹接口写入与删除。"""
import json
import urllib.request

BASE = "http://106.15.35.204:18480/api/v1/field/tracks"

payload = {
    "name": "部署自检轨迹",
    "src": "record",
    "points_json": json.dumps([[29.65, 91.10, 3650, None], [29.66, 91.12, 3660, None]]),
    "point_count": 2,
    "distance_km": 2.18,
    "duration_min": 35,
    "gain_m": 10,
}
req = urllib.request.Request(BASE, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=30) as r:
    created = json.loads(r.read())
print("POST ->", created["id"], created["name"])

with urllib.request.urlopen(BASE, timeout=30) as r:
    tracks = json.loads(r.read())
print("GET ->", len(tracks), "条:", [t["name"] for t in tracks])

req = urllib.request.Request(f"{BASE}/{created['id']}", method="DELETE")
with urllib.request.urlopen(req, timeout=30) as r:
    print("DELETE ->", r.read().decode())

with urllib.request.urlopen(BASE, timeout=30) as r:
    print("清理后 ->", json.loads(r.read()))
