# -*- coding: utf-8 -*-
"""生产服务器完整备份：sqlite在线备份 + 打包代码/媒体/配置 + 下载到本地 D:\\lasa-backups。"""
import os, sys, time, paramiko

HOST = "106.15.35.204"
PASS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lasa_pass"), encoding="utf-8").read().strip()
TS = time.strftime("%Y%m%d-%H%M%S")
RDIR = f"/opt/backups/lasa-backup-{TS}"
TAR = f"{RDIR}.tar.gz"
LOCAL_DIR = r"D:\lasa-backups"

def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, 22, "root", PASS, timeout=20)
log("SSH 已连接")

cmds = [
    f"mkdir -p {RDIR}",
    # 数据库一致性备份（不停机）
    f"sqlite3 /opt/lasa-nanshan-platform/data/lasa_nanshan.db \".backup '{RDIR}/lasa_nanshan.db'\" && echo DB_BACKUP_OK",
    f"sqlite3 {RDIR}/lasa_nanshan.db 'PRAGMA integrity_check;' | head -1",
    # 服务器配置留档
    "cp /etc/nginx/conf.d/*.conf " + RDIR + "/ 2>/dev/null; cp /etc/supervisord.d/*.ini " + RDIR + "/ 2>/dev/null; cp /etc/supervisor/conf.d/*.ini " + RDIR + "/ 2>/dev/null; ls " + RDIR,
    # 打总包：平台（排除 venv/node_modules/缓存/日志）+ 一致性库副本
    f"tar czf {TAR} --exclude='*/venv' --exclude='*/node_modules' --exclude='*/__pycache__' --exclude='*.log' "
    f"-C /opt lasa-nanshan-platform -C /opt/backups lasa-backup-{TS} && echo TAR_OK",
    f"ls -lh {TAR}",
]
for cmd in cmds:
    _, o, e = c.exec_command(cmd, timeout=280)
    out = o.read().decode().strip()
    log(f"$ {cmd[:80]}\n{out}")
    err = e.read().decode().strip()
    if err:
        log("STDERR: " + err[:300])

# 下载到本地
os.makedirs(LOCAL_DIR, exist_ok=True)
local = os.path.join(LOCAL_DIR, os.path.basename(TAR))
sftp = c.open_sftp()
size = sftp.stat(TAR).st_size
log(f"开始下载 {size/1e6:.1f} MB -> {local}")
t0 = time.time()
sftp.get(TAR, local)
log(f"下载完成 用时 {time.time()-t0:.0f}s")
sftp.close(); c.close()

# 本地校验
import tarfile
with tarfile.open(local, "r:gz") as t:
    names = t.getnames()
log(f"本地校验: {len(names)} 个条目")
key = [n for n in names if n.endswith("lasa_nanshan.db")]
log("含数据库副本: " + str(key))
import sqlite3
with tarfile.open(local, "r:gz") as t:
    t.extract(key[0], LOCAL_DIR)
dbp = os.path.join(LOCAL_DIR, key[0])
con = sqlite3.connect(dbp)
log("DB integrity_check: " + con.execute("PRAGMA integrity_check").fetchone()[0])
tabs = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
log(f"DB 表({len(tabs)}): " + ",".join(tabs[:12]))
con.close()
os.remove(dbp)

# 保留策略：本地与服务器各留最近 4 份
KEEP = 4
import glob, re
local_baks = sorted(glob.glob(os.path.join(LOCAL_DIR, "lasa-backup-*.tar.gz")))
for old in local_baks[:-KEEP]:
    os.remove(old)
    log("本地清理: " + os.path.basename(old))

c2 = paramiko.SSHClient(); c2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c2.connect(HOST, 22, "root", PASS, timeout=20)
_, o, _ = c2.exec_command("ls -d /opt/backups/lasa-backup-* 2>/dev/null | sort", timeout=30)
items = o.read().decode().split()
for old in items[:-KEEP * 2]:  # 每份含 dir + tar.gz 两个条目
    c2.exec_command(f"rm -rf '{old}'", timeout=60)
    log("服务器清理: " + old)
c2.close()
log("DONE")
