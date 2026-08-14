"""下载 Gradle 8.7 并解压到 C:\\tools\\gradle-8.7。"""
import os, shutil, zipfile, requests, subprocess

TOOLS = r"C:\tools"
ZIP = os.path.join(TOOLS, "gradle.zip")
DEST = os.path.join(TOOLS, "gradle-8.7")
URL = "https://services.gradle.org/distributions/gradle-8.7-bin.zip"

if not os.path.exists(os.path.join(DEST, "bin", "gradle.bat")):
    done = os.path.getsize(ZIP) if os.path.exists(ZIP) else 0
    headers = {"Range": f"bytes={done}-"} if done else {}
    with requests.get(URL, headers=headers, stream=True, timeout=(20, 60), allow_redirects=True) as r:
        r.raise_for_status()
        got = done
        with open(ZIP, "ab" if done else "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk); got += len(chunk)
    print("下载完成", round(got / 1e6, 1), "MB，解压 ...")
    tmp = os.path.join(TOOLS, "_g_tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    with zipfile.ZipFile(ZIP) as z:
        z.extractall(tmp)
    shutil.rmtree(DEST, ignore_errors=True)
    shutil.move(os.path.join(tmp, "gradle-8.7"), DEST)
    shutil.rmtree(tmp, ignore_errors=True)
env = dict(os.environ, JAVA_HOME=r"C:\tools\jdk17")
out = subprocess.run([os.path.join(DEST, "bin", "gradle.bat"), "-v"], capture_output=True, text=True, env=env, timeout=180)
print((out.stdout or out.stderr)[:400])
