"""v1.2.0 后端部署：上传识别/语音新代码到生产服务器并迁移数据库。

一次性脚本（2026-08-15）：
1. 服务器端先打包备份现有 backend/app 代码
2. SFTP 上传 6 个改动/新增文件
3. 把 v2 的 DEEPSEEK_*（智谱GLM）配置追加进生产 .env（缺的才追加）
4. SQLite 迁移：patrol_photos 增加 8 个物种识别列（幂等，逐列检查）
5. 重启生产后端并做健康检查

用法: python scripts/deploy_v120_backend.py
"""
import sys, time
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parent.parent
PASS = (ROOT / "scripts" / ".lasa_pass").read_text(encoding="utf-8").strip()
HOST = "106.15.35.204"
REMOTE_BACKEND = "/opt/lasa-nanshan-platform/backend"
V2_ENV = Path("C:/tools/v2src/env.txt")  # 含智谱 GLM key（敏感，勿提交）

FILES = [
    ("backend/app/models.py", f"{REMOTE_BACKEND}/app/models.py"),
    ("backend/app/core/config.py", f"{REMOTE_BACKEND}/app/core/config.py"),
    ("backend/app/main.py", f"{REMOTE_BACKEND}/app/main.py"),
    ("backend/app/routers/patrol_photos.py", f"{REMOTE_BACKEND}/app/routers/patrol_photos.py"),
    ("backend/app/routers/voice.py", f"{REMOTE_BACKEND}/app/routers/voice.py"),
    ("backend/app/services/plant_identifier.py", f"{REMOTE_BACKEND}/app/services/plant_identifier.py"),
    ("backend/app/services/voice_transcriber.py", f"{REMOTE_BACKEND}/app/services/voice_transcriber.py"),
]

MIGRATION_PY = r'''
import sqlite3
db = sqlite3.connect("/opt/lasa-nanshan-platform/data/lasa_nanshan.db")  # .env DATABASE_URL 指向的真库
cols = [r[1] for r in db.execute("PRAGMA table_info(patrol_photos)").fetchall()]
adds = [
    ("species", "VARCHAR(200) DEFAULT ''"),
    ("scientific_name", "VARCHAR(200) DEFAULT ''"),
    ("species_confidence", "FLOAT"),
    ("species_family", "VARCHAR(100) DEFAULT ''"),
    ("species_genus", "VARCHAR(100) DEFAULT ''"),
    ("species_features", "TEXT DEFAULT ''"),
    ("identified_at", "DATETIME"),
    ("identified_by", "VARCHAR(50) DEFAULT ''"),
]
for name, decl in adds:
    if name in cols:
        print(f"skip {name} (exists)")
    else:
        db.execute(f"ALTER TABLE patrol_photos ADD COLUMN {name} {decl}")
        print(f"added {name}")
db.commit()
print("patrol_photos cols now:", len([r[1] for r in db.execute("PRAGMA table_info(patrol_photos)").fetchall()]))
db.close()
print("MIGRATION_DONE")
'''


def run(ssh, cmd, timeout=120):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    rc = out.channel.recv_exit_status()
    o, e = out.read().decode("utf-8", "replace"), err.read().decode("utf-8", "replace")
    return rc, o, e


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username="root", password=PASS, timeout=20)
    sftp = ssh.open_sftp()
    ts = time.strftime("%Y%m%d-%H%M%S")

    print(f"[1/6] 服务器端备份现有代码 -> /root/lasa-app-backup-{ts}.tar.gz")
    rc, o, e = run(ssh, f"tar czf /root/lasa-app-backup-{ts}.tar.gz -C /opt/lasa-nanshan-platform/backend app")
    assert rc == 0, e

    print("[2/6] 上传 7 个后端文件...")
    for local, remote in FILES:
        sftp.put(str(ROOT / local), remote)
        print("  put", local)

    print("[3/6] 追加 .env 识别配置（仅缺省项）...")
    v2 = {}
    for line in V2_ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            v2[k.strip()] = v.strip()
    want = ["DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL", "DEEPSEEK_TIMEOUT"]
    rc, cur, _ = run(ssh, f"cat {REMOTE_BACKEND}/.env 2>/dev/null || true")
    append_lines = []
    for k in want:
        if k + "=" not in cur:
            if k not in v2:
                print(f"  !! v2 env 缺少 {k}，跳过")
                continue
            append_lines.append(f"{k}={v2[k]}")
            print(f"  + {k}")
        else:
            print(f"  = {k} 已存在")
    if "VOICE_ASR_ENABLED=" not in cur:
        append_lines.append("VOICE_ASR_ENABLED=false")  # faster-whisper 未装，显式关闭转写
        print("  + VOICE_ASR_ENABLED=false")
    if append_lines:
        payload = "\\n".join(append_lines)
        rc, o, e = run(ssh, f"printf '{payload}\\n' >> {REMOTE_BACKEND}/.env")
        assert rc == 0, e

    print("[4/6] SQLite 迁移 patrol_photos 物种列...")
    run(ssh, "rm -f /opt/lasa-nanshan-platform/backend/data/lasa_nanshan.db")  # 清理误建的0字节库（真库在 platform/data/）
    sftp.putfo(__import__("io").BytesIO(MIGRATION_PY.encode()), "/tmp/mig_v120.py")
    rc, o, e = run(ssh, "python3 /tmp/mig_v120.py")
    print(o)
    assert rc == 0 and "MIGRATION_DONE" in o, e

    print("[5/6] 重启生产后端...")
    rc, o, e = run(ssh, "supervisorctl restart lasa-nanshan-backend")
    print(o, e)
    time.sleep(6)

    print("[6/6] 健康检查...")
    rc, o, e = run(ssh, "curl -s -m 10 http://127.0.0.1:18481/api/v1/health")
    print("health:", o[:200])
    rc, o2, _ = run(ssh, "curl -s -m 10 -o /dev/null -w '%{http_code}' http://127.0.0.1:18481/api/v1/voice")
    print("voice route http_code:", o2)
    sftp.close()
    ssh.close()
    print("DEPLOY_DONE")


if __name__ == "__main__":
    main()
