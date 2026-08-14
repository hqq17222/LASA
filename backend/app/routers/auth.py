from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import security as sec
from app.models import User
from app.schemas import LoginIn, LoginOut, UserInfo

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginOut, summary="登录获取令牌")
def login(data: LoginIn, db: Session = Depends(get_db)):
    uname = data.username.strip()
    u = db.query(User).filter(User.username == uname).first()
    if not u or not sec.verify_password(data.password.strip(), u.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not u.is_active:
        raise HTTPException(status_code=403, detail="账户已停用，请联系管理员")
    token = sec.create_token(db, u)
    return {"token": token, "user": u}


@router.get("/me", response_model=UserInfo, summary="当前登录用户")
def me(request: Request):
    return request.state.user


@router.post("/logout", summary="登出")
def logout(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if token:
        sec.revoke_token(db, token)
    return {"detail": "logged out"}
