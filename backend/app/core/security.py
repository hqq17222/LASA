# 认证与权限：PBKDF2 密码哈希 + 数据库令牌 + 角色等级
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, AuthToken

ROLE_LEVELS = {"viewer": 1, "analyst": 2, "manager": 3, "admin": 4}
ROLE_NAMES = {"viewer": "只读访客", "analyst": "数据分析", "manager": "项目主管", "admin": "管理员"}
TOKEN_DAYS = 7


def hash_password(pw: str, salt: str = None) -> str:
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 60000).hex()
    return f"{salt}${h}"


def verify_password(pw: str, stored: str) -> bool:
    try:
        salt, h = stored.split("$", 1)
    except ValueError:
        return False
    calc = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 60000).hex()
    return hmac.compare_digest(calc, h)


def create_token(db: Session, user: User) -> str:
    tok = secrets.token_hex(32)
    db.add(AuthToken(token=tok, user_id=user.id, expires_at=datetime.utcnow() + timedelta(days=TOKEN_DAYS)))
    db.commit()
    return tok


def get_user_by_token(db: Session, token: str):
    if not token:
        return None
    t = db.query(AuthToken).filter(AuthToken.token == token).first()
    if not t or t.expires_at < datetime.utcnow():
        return None
    u = db.query(User).get(t.user_id)
    if not u or not u.is_active:
        return None
    return u


def revoke_token(db: Session, token: str):
    db.query(AuthToken).filter(AuthToken.token == token).delete()
    db.commit()


def role_level(role: str) -> int:
    return ROLE_LEVELS.get(role, 1)
