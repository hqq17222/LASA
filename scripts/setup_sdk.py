"""下载 Android cmdline-tools 并部署到 C:\\tools\\android-sdk\\cmdline-tools\\latest。"""
import os, shutil, zipfile, requests, subprocess

SDK = r"C:\tools\android-sdk"
ZIP = os.path.join(SDK, "cmdtools.zip")
DEST = os.path.join(SDK, "cmdline-tools", "latest")
URL = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"

os.makedirs(SDK, exist_ok=True)
if not os.path.exists(os.path.join(DEST, "bin", "sdkmanager.bat")):
    done = os.path.getsize(ZIP) if os.path.exists(ZIP) else 0
    headers = {"Range": f"bytes={done}-"} if done else {}
    with requests.get(URL, headers=headers, stream=True, timeout=(20, 60)) as r:
        r.raise_for_status()
        got = done
        with open(ZIP, "ab" if done else "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk); got += len(chunk)
    print("下载完成", round(got / 1e6, 1), "MB，解压 ...")
    tmp = os.path.join(SDK, "_ct_tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    with zipfile.ZipFile(ZIP) as z:
        z.extractall(tmp)
    # zip 内含 cmdline-tools/ 目录，需放到 cmdline-tools/latest 下
    shutil.rmtree(os.path.join(SDK, "cmdline-tools"), ignore_errors=True)
    os.makedirs(os.path.join(SDK, "cmdline-tools"), exist_ok=True)
    shutil.move(os.path.join(tmp, "cmdline-tools"), DEST)
    shutil.rmtree(tmp, ignore_errors=True)
env = dict(os.environ, JAVA_HOME=r"C:\tools\jdk17")
out = subprocess.run([os.path.join(DEST, "bin", "sdkmanager.bat"), "--version"],
                     capture_output=True, text=True, env=env, timeout=120)
print("sdkmanager:", (out.stdout or out.stderr).strip()[:200])
