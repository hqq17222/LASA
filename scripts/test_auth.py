"""外网验证认证与权限分级。"""
import json
import urllib.request
import urllib.error

BASE = "http://106.15.35.204:18480/api/v1"

def call(method, path, token=None, body=None):
    req = urllib.request.Request(BASE + path, method=method)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    data = json.dumps(body).encode() if body is not None else None
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:120]

print("1 未登录访问 projects:", call("GET", "/projects"))
s, login = call("POST", "/auth/login", body={"username": "admin", "password": "Lasa@2026"})
print("2 管理员登录:", s, login.get("user"))
tok = login["token"]
print("3 带令牌访问 projects:", call("GET", "/projects", tok)[0])
s, users = call("GET", "/users", tok)
print("4 用户列表:", s, [(u["username"], u["role"]) for u in users])
s, viewer = call("POST", "/users", tok, body={"username": "guest01", "password": "guest123", "display_name": "访客一号", "role": "viewer"})
print("5 创建只读访客:", s, viewer.get("username") if isinstance(viewer, dict) else viewer)
s, vlogin = call("POST", "/auth/login", body={"username": "guest01", "password": "guest123"})
vtok = vlogin["token"]
print("6 访客登录:", s, vlogin.get("user"))
print("7 访客读 projects:", call("GET", "/projects", vtok)[0])
print("8 访客写 projects(应403):", call("POST", "/projects", vtok, body={"name": "x", "code": "x1"}))
print("9 访客访问 users(应403):", call("GET", "/users", vtok))
s, wrong = call("POST", "/auth/login", body={"username": "admin", "password": "wrong"})
print("10 错误密码(应401):", s, wrong)
s, _ = call("DELETE", f"/users/{viewer['id']}", tok)
print("11 清理测试访客:", s)
print("12 登录页:", end=" ")
with urllib.request.urlopen("http://106.15.35.204:18480/login", timeout=30) as r:
    print(r.status)
