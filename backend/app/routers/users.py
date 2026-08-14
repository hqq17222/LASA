from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import security as sec
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["用户管理"])

VALID_ROLES = {"admin", "manager", "analyst", "viewer"}


@router.get("", response_model=List[UserResponse], summary="用户列表")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()


@router.post("", response_model=UserResponse, summary="创建用户")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="无效的用户组")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")
    u = User(username=data.username, password_hash=sec.hash_password(data.password),
             display_name=data.display_name or data.username, role=data.role)
    db.add(u); db.commit(); db.refresh(u)
    return u


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户")
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    u = db.query(User).get(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    if data.role is not None:
        if data.role not in VALID_ROLES:
            raise HTTPException(status_code=400, detail="无效的用户组")
        u.role = data.role
    if data.display_name is not None:
        u.display_name = data.display_name
    if data.is_active is not None:
        u.is_active = data.is_active
    if data.password:
        if len(data.password) < 6:
            raise HTTPException(status_code=400, detail="密码至少 6 位")
        u.password_hash = sec.hash_password(data.password)
    db.commit(); db.refresh(u)
    return u


@router.delete("/{user_id}", summary="删除用户")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).get(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    admins = db.query(User).filter(User.role == "admin", User.is_active == True).count()
    if u.role == "admin" and admins <= 1:
        raise HTTPException(status_code=400, detail="至少保留一名管理员")
    db.delete(u); db.commit()
    return {"detail": "deleted"}
