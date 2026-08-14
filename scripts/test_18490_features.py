# -*- coding: utf-8 -*-
"""18490 新功能端到端测试：语音备注 / 智能识别 / 物种字段。"""
import json, time, urllib.request, urllib.parse, uuid

B = "http://106.15.35.204:18490"

def req(method, path, tok=None, data=None, ctype="application/json", raw=None):
    r = urllib.request.Request(B+path, method=method,
        data=raw if raw is not None else (json.dumps(data).encode() if data is not None else None),
        headers={**({"Authorization": f"Bearer {tok}"} if tok else {}),
                 **({"Content-Type": ctype} if (data is not None or raw is not None) else {})})
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return resp.status, resp.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:500]

def multipart(fields, files):
    boundary = uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, (fname, blob, mime) in files.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{fname}"\r\nContent-Type: {mime}\r\n\r\n'.encode() + blob + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"

# 登录
st, r = req("POST", "/api/v1/auth/login", data={"username": "admin", "password": "30010223"})
tok = json.loads(r)["token"]
print("登录", st)

# ---------- 1. 语音备注 ----------
print("\n===== 1. 语音备注 =====")
import wave, struct, math, io
buf = io.BytesIO()
with wave.open(buf, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
    w.writeframes(b"".join(struct.pack("<h", int(3000*math.sin(2*math.pi*440*t/16000))) for t in range(16000)))
wav = buf.getvalue()
body, ct = multipart({"note": "测试语音备注：云杉样地1号"}, {"file": ("test_voice.wav", wav, "audio/wav")})
st, r = req("POST", "/api/v1/voice/upload", tok, raw=body, ctype=ct)
print("上传语音:", st, r[:300])
vid = None
try: vid = json.loads(r).get("id")
except Exception: pass
st, r = req("GET", "/api/v1/voice", tok)
print("语音列表:", st, r[:400])
if vid:
    st, r = req("GET", f"/api/v1/voice/{vid}", tok)
    print("语音详情:", st, r[:400])

# ---------- 2. 智能识别（真实外业照片 id=1） ----------
print("\n===== 2. 智能识别（真实照片 id=1） =====")
st, r = req("POST", "/api/v1/patrol-photos/1/identify", tok, data={"context": "拉萨南北山样地"})
print("识别:", st, r[:600])

# ---------- 3. 物种字段持久化 + 地图弹窗数据源 ----------
print("\n===== 3. 物种字段 =====")
st, r = req("GET", "/api/v1/patrol-photos/1", tok)
d = json.loads(r) if st == 200 else {}
print("照片详情物种字段:", json.dumps({k: d.get(k) for k in ["species","scientific_name","species_confidence","species_family","species_genus","identified_at","identified_by"]}, ensure_ascii=False))
# 手动修正接口
st, r = req("PUT", "/api/v1/patrol-photos/1/species", tok, data={"species": d.get("species") or "云杉", "scientific_name": d.get("scientific_name") or "Picea sp."})
print("PUT species:", st, r[:300])
# 地图弹窗数据源（列表接口是否带物种）
st, r = req("GET", "/api/v1/patrol-photos?limit=3", tok)
lst = json.loads(r)
p1 = [p for p in lst if p["id"] == 1]
print("列表中照片1的物种字段:", json.dumps({k: p1[0].get(k) for k in ["species","species_confidence","scientific_name"]}, ensure_ascii=False) if p1 else "未找到")

# ---------- 清理测试语音 ----------
if vid:
    st, r = req("DELETE", f"/api/v1/voice/{vid}", tok)
    print("\n清理测试语音:", st)
print("\nTEST_DONE")
