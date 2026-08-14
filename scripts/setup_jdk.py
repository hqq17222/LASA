"""下载 Temurin JDK 17（requests 流式 + Range 续传）并解压到 C:\\tools\\jdk17。"""
import os, sys, shutil, zipfile, requests

TOOLS = r"C:\tools"
ZIP = os.path.join(TOOLS, "jdk17.zip")
DEST = os.path.join(TOOLS, "jdk17")
URL = "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse"

os.makedirs(TOOLS, exist_ok=True)
if not os.path.isdir(DEST):
    done = os.path.getsize(ZIP) if os.path.exists(ZIP) else 0
    headers = {"Range": f"bytes={done}-"} if done else {}
    mode = "ab" if done else "wb"
    print(f"下载 JDK17（已存 {done/1e6:.0f}MB，续传）...")
    with requests.get(URL, headers=headers, stream=True, timeout=(20, 60), allow_redirects=True) as r:
        r.raise_for_status()
        total = r.headers.get("Content-Range", "").split("/")[-1] or r.headers.get("Content-Length", "?")
        print("总大小约", total, "bytes" if total != "?" else "")
        got = done
        with open(ZIP, mode) as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk); got += len(chunk)
                if got % (20 << 20) < (1 << 20):
                    print(f"  {got/1e6:.0f} MB")
    print("下载完成", got / 1e6, "MB，解压 ...")
    tmp = os.path.join(TOOLS, "_jdk_tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    with zipfile.ZipFile(ZIP) as z:
        z.extractall(tmp)
    inner = [d for d in os.listdir(tmp) if d.startswith("jdk")][0]
    shutil.move(os.path.join(tmp, inner), DEST)
    shutil.rmtree(tmp, ignore_errors=True)
import subprocess
out = subprocess.run([os.path.join(DEST, "bin", "java.exe"), "-version"], capture_output=True, text=True)
print("JAVA OK:", (out.stderr or out.stdout).splitlines()[0])
print("JAVA_HOME =", DEST)
