"""Deploy 拉萨南北山生态监测评估系统 to Alibaba Cloud Linux 3 server."""
import os, sys, paramiko, time, json
from pathlib import Path

# Windows 控制台默认 GBK，强制 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HOST = '106.15.35.204'
PORT = 22
USER = 'root'
PASSWORD = os.environ.get('LASA_PASS', '')
APP_DIR = '/opt/lasa-nanshan-platform'
API_PREFIX = "/api/v1"
API_PORT = 18481
NGINX_PORT = 18480
LOCAL_BASE = Path(__file__).resolve().parent.parent

if not PASSWORD:
    print("请设置环境变量 LASA_PASS（服务器 root 密码）")
    sys.exit(1)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, look_for_keys=False, allow_agent=False, timeout=15)
print(f"已连接 {HOST}")

def cmd(c, timeout=120):
    print(f"\n$ {c}")
    sys.stdout.flush()
    stdin, stdout, stderr = ssh.exec_command(c, timeout=timeout, get_pty=False)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out[-1000:])
    if err and ec != 0:
        print(f"WARN {err[-500:]}")
    sys.stdout.flush()
    return ec, out, err

print("\n=== 1. 清理并创建目录 ===")
cmd(f"rm -rf {APP_DIR}")
cmd(f"mkdir -p {APP_DIR}/{{backend,frontend,scripts,data/uploads,data/logs,data/reports}}")

print("\n=== 2. 上传后端代码 ===")
sftp = ssh.open_sftp()

def upload_dir(local_dir, remote_dir):
    for root, dirs, files in os.walk(local_dir):
        rel = os.path.relpath(root, local_dir)
        rel_parts = Path(rel).parts
        if any(p in rel_parts for p in ['node_modules', 'venv', '.venv', '__pycache__', '.git', 'dist', '.idea']):
            continue
        if rel == '.':
            remote_root = remote_dir
        else:
            remote_root = remote_dir + '/' + rel.replace('\\', '/')
        try:
            sftp.stat(remote_root)
        except:
            cmd(f"mkdir -p {remote_root}")
        for f in files:
            if f.endswith(('.pyc', '.log', '.tmp')):
                continue
            local_path = os.path.join(root, f)
            remote_path = remote_root + '/' + f
            sftp.put(local_path, remote_path)


upload_dir(LOCAL_BASE / 'backend', APP_DIR + '/backend')
upload_dir(LOCAL_BASE / 'frontend', APP_DIR + '/frontend')
upload_dir(LOCAL_BASE / 'scripts', APP_DIR + '/scripts')
sftp.close()
print("上传完成")

print("\n=== 3. 安装 Python 依赖 ===")
cmd(f"cd {APP_DIR}/backend && python3.11 -m venv venv", 60)
cmd(f"cd {APP_DIR}/backend && venv/bin/pip install --upgrade pip setuptools wheel -q", 120)
cmd(f"cd {APP_DIR}/backend && venv/bin/pip install -r requirements.txt -q", 300)

print("\n=== 4. 写入 .env ===")
env_content = f"""APP_NAME=拉萨南北山生态监测评估系统集成平台
DEBUG=false
HOST=0.0.0.0
PORT={API_PORT}
API_PREFIX=/api/v1
DATABASE_URL=sqlite:///{APP_DIR}/data/lasa_nanshan.db
LOG_LEVEL=INFO
GEE_SERVICE_ACCOUNT=
MODEL_GATEWAY_TIMEOUT=120
"""
sftp = ssh.open_sftp()
with sftp.open(f"{APP_DIR}/backend/.env", 'w') as f:
    f.write(env_content)

print("\n=== 5. 初始化数据库并加载种子数据 ===")
init_script = f"""import sys; sys.path.insert(0, '{APP_DIR}/backend')
from app.core.database import init_db
import seed
init_db()
seed.run_seed()
print('DB initialized and seeded')
"""
with sftp.open(f"{APP_DIR}/backend/init_db.py", 'w') as f:
    f.write(init_script)
sftp.close()

cmd(f"cd {APP_DIR}/backend && venv/bin/python init_db.py", 120)

print("\n=== 6. 构建前端 ===")
# 使用 npm 官方/国内镜像都可以，这里使用 npmmirror
npm_cmd = f"cd {APP_DIR}/frontend && npm install --no-audit --no-fund --registry=https://registry.npmmirror.com --timeout=100000"
# npm install 可能占用较多内存，若 OOM 可换 workers=1
ec, out, err = cmd(npm_cmd, 300)
if ec != 0:
    print("npm install 失败，尝试只安装必要运行时包...")
    cmd(f"cd {APP_DIR}/frontend && npm install --no-audit --no-fund --prefer-offline --registry=https://registry.npmmirror.com", 300)

# 构建（Vite 4 + Rollup 3 纯 JS，无需额外平台包）
cmd(f"cd {APP_DIR}/frontend && npx vite build", 180)

print(f"\n=== 7. 配置 Nginx（新端口 {NGINX_PORT}，不干扰现有网站） ===")
nginx_conf = f"""server {{
    listen {NGINX_PORT};
    server_name {HOST};
    client_max_body_size 100M;
    root {APP_DIR}/frontend/dist;
    index index.html;
    location / {{ try_files $uri $uri/ /index.html; }}
    location /api/ {{
        proxy_pass http://127.0.0.1:{API_PORT}/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }}
    location /docs {{ proxy_pass http://127.0.0.1:{API_PORT}/docs; }}
    location /openapi.json {{ proxy_pass http://127.0.0.1:{API_PORT}/openapi.json; }}
    location /static/ {{ alias {APP_DIR}/data/uploads/; expires 7d; }}
}}"""
sftp = ssh.open_sftp()
with sftp.open("/etc/nginx/conf.d/lasa-nanshan-platform.conf", 'w') as f:
    f.write(nginx_conf)
sftp.close()

cmd("nginx -t")
cmd("systemctl reload nginx")

print("\n=== 8. 配置 Supervisor ===")
sup_conf = f"""[program:lasa-nanshan-backend]
command={APP_DIR}/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port {API_PORT} --workers 1
directory={APP_DIR}/backend
user=root
autostart=true
autorestart=true
startretries=3
stderr_logfile={APP_DIR}/data/logs/backend.err.log
stdout_logfile={APP_DIR}/data/logs/backend.out.log
environment=PYTHONPATH="{APP_DIR}/backend"
"""
sftp = ssh.open_sftp()
with sftp.open("/etc/supervisord.d/lasa-nanshan-platform.ini", 'w') as f:
    f.write(sup_conf)
sftp.close()

cmd(f"mkdir -p {APP_DIR}/data/logs")
cmd("supervisorctl reread")
cmd("supervisorctl update")
cmd("supervisorctl restart lasa-nanshan-backend || supervisorctl start lasa-nanshan-backend")
time.sleep(5)

print("\n=== 9. 验证 ===")
ec, out, err = cmd(f"curl -s http://127.0.0.1:{API_PORT}{API_PREFIX}/health")
print("健康检查:", out)

try:
    d = json.loads(out)
    print(f"\n{'='*50}")
    print(f"部署完成")
    print(f"   访问地址: http://{HOST}:{NGINX_PORT}")
    print(f"   API 文档: http://{HOST}:{NGINX_PORT}/docs")
    print(f"   健康检查: {d}")
    print(f"{'='*50}")
except Exception as e:
    print(f"\n部署完成，但健康检查异常: {e}")
    print(f"   请手动检查: ssh root@{HOST} -p {PORT}")

ssh.close()
