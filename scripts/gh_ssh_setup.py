# -*- coding: utf-8 -*-
"""生成SSH密钥、添加为LASA仓库部署密钥、扫描github.com主机指纹。"""
import json, subprocess, sys, urllib.request

TOKEN = json.load(open(r"C:\tools\gjob\gh_token.json"))["token"]
H = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
     "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"}

KEY = r"C:\tools\gh_lasa_key"
r = subprocess.run(["ssh-keygen", "-t", "ed25519", "-f", KEY, "-N", "", "-C", "lasa-deploy"],
                   capture_output=True, text=True)
print("keygen:", r.returncode)
pub = open(KEY + ".pub").read().strip()

req = urllib.request.Request("https://api.github.com/repos/hqq17222/LASA/keys",
                             data=json.dumps({"title": "lasa-deploy", "key": pub, "read_only": False}).encode(),
                             headers=H, method="POST")
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("deploy key 已添加:", resp.status)
except urllib.error.HTTPError as e:
    body = e.read().decode()[:200]
    print("deploy key:", e.code, body)
    if e.code != 422:
        sys.exit(1)

print("--- ssh-keyscan github.com ---")
r = subprocess.run(["ssh-keyscan", "-t", "ed25519", "github.com"], capture_output=True, text=True, timeout=30)
print(r.stdout, r.stderr[:200])
if r.stdout:
    open(r"C:\tools\gjob\gh_hosts", "w").write(r.stdout)
    r2 = subprocess.run(["ssh-keygen", "-lf", r"C:\tools\gjob\gh_hosts"], capture_output=True, text=True)
    print("指纹:", r2.stdout)
