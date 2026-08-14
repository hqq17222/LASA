# -*- coding: utf-8 -*-
"""用 dulwich（纯Python git）推送 C:\\tools\\LASA main 到 GitHub，绕过 TLS 拦截。"""
import json, os, urllib.request
os.makedirs(r"C:\tools\nohome", exist_ok=True)
os.environ["HOME"] = r"C:\tools\nohome"  # 让 dulwich 读不到全局 .gitconfig 里的代理
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"
urllib.request.getproxies = lambda: {}
urllib.request.getproxies_registry = lambda: {}
urllib.request.getproxies_environment = lambda: {}
from dulwich import porcelain
from dulwich.config import StackedConfig, ConfigDict

def _empty_default(cls):
    s = StackedConfig.__new__(StackedConfig)
    s.backends = [ConfigDict()]
    return s
StackedConfig.default = classmethod(_empty_default)  # 无视所有 gitconfig
StackedConfig.default_backends = classmethod(lambda cls: [ConfigDict()])  # get_config_stack 走这里

TOKEN = json.load(open(r"C:\tools\gjob\gh_token.json"))["token"]
URL = f"https://x-access-token:{TOKEN}@github.com/hqq17222/LASA.git"

def progress(msg):
    print("git:", msg.decode(errors="replace").strip() if isinstance(msg, bytes) else msg)

try:
    import urllib3
    urllib3.disable_warnings()
    pm = urllib3.PoolManager(cert_reqs="CERT_NONE", assert_hostname=False)  # 本机加速器MITM环境
    porcelain.push(r"C:\tools\LASA", URL, "refs/heads/main:refs/heads/main",
                   pool_manager=pm,
                   outstream=type("W", (), {"write": staticmethod(progress)})())
    print("PUSH_OK")
except Exception as e:
    msg = str(e).replace(TOKEN, "***")
    print("PUSH_FAIL:", msg[:300])
