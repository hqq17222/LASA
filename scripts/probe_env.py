import shutil, os, subprocess
print("java:", shutil.which("java"))
print("node:", shutil.which("node"))
print("npm:", shutil.which("npm"), shutil.which("npm.cmd"))
print("gradle:", shutil.which("gradle"))
print("ANDROID_HOME:", os.environ.get("ANDROID_HOME"))
print("ANDROID_SDK_ROOT:", os.environ.get("ANDROID_SDK_ROOT"))
for p in [os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk"), r"C:\Program Files\Android", os.path.expandvars(r"%USERPROFILE%\AppData\Local\Android\Sdk")]:
    print(p, "exists" if os.path.isdir(p) else "-")
try:
    out = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=15)
    print("java version:", (out.stderr or out.stdout).splitlines()[0])
except Exception as e:
    print("java run fail:", e)
