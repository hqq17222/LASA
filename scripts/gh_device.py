# -*- coding: utf-8 -*-
"""GitHub OAuth Device Flow：request 申请设备码 / poll 轮询换取 token。"""
import json, sys, time, urllib.request, urllib.parse

CID = "178c6fc778ccc68e1d6a"  # GitHub CLI 官方 OAuth App（公开 client_id，专用于设备流）
STATE = r"C:\tools\gjob\gh_device.json"

def post(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                                 headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

if sys.argv[1] == "request":
    d = post("https://github.com/login/device/code", {"client_id": CID, "scope": "repo"})
    if "device_code" not in d:
        print("FAIL:", d); sys.exit(1)
    json.dump(d, open(STATE, "w"))
    print("USER_CODE:", d["user_code"])
    print("URL:", d["verification_uri"])
    print("有效期:", d["expires_in"], "秒")
elif sys.argv[1] == "poll":
    d = json.load(open(STATE))
    r = post("https://github.com/login/oauth/access_token", {
        "client_id": CID, "device_code": d["device_code"],
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"})
    if "access_token" in r:
        print("TOKEN_OK")
        json.dump({"token": r["access_token"]}, open(r"C:\tools\gjob\gh_token.json", "w"))
    else:
        print("PENDING_OR_ERR:", r.get("error"))
