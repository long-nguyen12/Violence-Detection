from ast import Delete
from fastapi import Request, Response, Body, APIRouter, File, UploadFile, Depends, WebSocket, WebSocketDisconnect, HTTPException
from app.database.models import *
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
import cv2
from app.database.schemas import *
from pathlib import Path
from app.constants import *
from fastapi_pagination import Page, add_pagination, paginate, Params
from typing import Union, Any
import jwt
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.security import *
control_auth = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_token(username: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(
        seconds=60 * 60 * 24 * 3650  # Expired after 3 days
    )
    to_encode = {
        "exp": expire, "username": username
    }
    encoded_jwt = jwt.encode(
        to_encode, Constants.SECRET_KEY, algorithm=Constants.ALGORITHM)
    return encoded_jwt


@control_auth.post("/backend/api/user/register")
async def create(user: UserSchema, sess: Session = Depends(get_db)):
    try:
        user.password = generate_password_hash(user.password)
        new_user = User(username=user.username, password=user.password,
                        full_name=user.full_name, role=user.role, create_at=user.create_at)
        sess.add(new_user)
        sess.commit()
        sess.refresh(new_user)
        return new_user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)


@control_auth.post("/backend/api/user/login")
async def login(user_login: LoginSchema, sess: Session = Depends(get_db)):
    try:
        user = sess.query(User).filter(
            User.username == user_login.username).first()
        password = user_login.password
        if not user:
            raise HTTPException(status_code=401, detail="Wrong username")
        if not check_password_hash(user.password, password):
            raise HTTPException(status_code=401, detail="Wrong password")
        login_token = generate_token(user.username)
        return {
            "token": login_token
        }
    except Exception as e:
        print(e, "Error")
        raise HTTPException(status_code=500)


@control_auth.get("/backend/api/user/me")
async def get_profile(username: str = Depends(validate_token), sess: Session = Depends(get_db)):
    user = sess.query(User).filter(
        User.username == username).first()
    del(user.password)
    return user


@control_auth.delete("/backend/api/notification/{notification_id}")
async def update_notification(notification_id: str, sess: Session = Depends(get_db)):
    noti = sess.query(Notification).filter(
        Notification.id_notification == notification_id).first()
    if not noti:
        raise HTTPException(status_code=404, detail="Not found")
    sess.delete(noti)
    sess.commit()
    return {"ok": True}
