# -*- coding: utf-8 -*-
"""创建 GitHub 私有仓库 LASA 并推送 C:\\tools\\LASA 的 main 分支。"""
import json, subprocess, sys, urllib.request

TOKEN = json.load(open(r"C:\tools\gjob\gh_token.json"))["token"]
H = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
     "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"}

def api(method, url, data=None):
    req = urllib.request.Request("https://api.github.com" + url, method=method,
                                 data=json.dumps(data).encode() if data else None, headers=H)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

st, user = api("GET", "/user")
login = user.get("login")
print("GitHub 账号:", login, f"(status {st})")
if not login:
    sys.exit(1)

st, repo = api("POST", "/user/repos", {"name": "LASA", "private": True,
               "description": "拉萨南北山绿化监测平台 + 外业调查安卓App", "auto_init": False})
if st == 201:
    print("仓库已创建(私有):", repo["html_url"])
elif st == 422:
    print("仓库已存在，直接推送:", f"https://github.com/{login}/LASA")
else:
    print("建库失败:", st, repo); sys.exit(1)

url = f"https://github.com/{login}/LASA.git"
subprocess.run(["git", "-C", r"C:\tools\LASA", "remote", "remove", "origin"], capture_output=True)
subprocess.run(["git", "-C", r"C:\tools\LASA", "remote", "add", "origin", url], check=True)
p = subprocess.run(["git", "-C", r"C:\tools\LASA", "-c", f"http.extraHeader=Authorization: Bearer {TOKEN}",
                    "-c", "http.proxy=", "-c", "https.proxy=", "-c", "http.sslBackend=openssl",
                    "push", "-u", "origin", "main"], capture_output=True, text=True)
print(p.stdout.strip())
err = p.stderr.replace(TOKEN, "***")
print(err.strip()[-500:])
print("PUSH_OK" if p.returncode == 0 else "PUSH_FAIL")
