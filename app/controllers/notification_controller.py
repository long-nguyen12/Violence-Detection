from ast import Constant
from cmath import log
from decimal import Decimal
from email.mime import image
import os
from fastapi import Request, Response, Body, APIRouter, File, UploadFile, Depends, WebSocket, WebSocketDisconnect, HTTPException
from app.database.models import *
import time
from typing import Union
from tempfile import NamedTemporaryFile
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
import cv2
from app.database.schemas import *
from pathlib import Path
from app.constants import *
import aiofiles
from fastapi_pagination import Page, add_pagination, paginate, Params

control_notification = APIRouter()

SUB_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()
PARENT_PATH = SUB_PATH.parent.absolute()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@control_notification.post("/backend/api/notification")
async def create(file: Union[UploadFile, None] = None, sess: Session = Depends(get_db)):
    print(file)
    if not file:
        raise HTTPException(status_code=404, detail="Image not found")
    elif not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        raise HTTPException(status_code=401, detail="Wrong format")
    else:
        file_copy = os.path.join(
            PARENT_PATH, Constants.PUBLIC_FOLDER + file.filename)
        try:
            async with aiofiles.open(file_copy, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            now = datetime.now()
            iso_date = now.isoformat()

            noti = Notification(
                image=file.filename, create_at=iso_date, confirmed=0)
            sess.add(noti)
            sess.commit()
            sess.refresh(noti)
            return {"noti": noti}
        except:
            raise HTTPException(status_code=500)


@control_notification.get("/backend/api/notification", response_model=Page[NotificationSchema])
async def get_nitifications(params: Params = Depends(), sess: Session = Depends(get_db)):
    noti = sess.query(Notification).all()
    if not noti:
        raise HTTPException(status_code=404, detail="Not found")
    noti = noti[::-1]
    return paginate(noti, params)


@control_notification.put("/backend/api/notification/{notification_id}")
async def update_notification(notification_id: str, sess: Session = Depends(get_db)):
    noti = sess.query(Notification).filter(
        Notification.id_notification == notification_id).first()
    if not noti:
        raise HTTPException(status_code=404, detail="Not found")
    noti.confirmed = 1
    sess.add(noti)
    sess.commit()
    sess.refresh(noti)
    return noti

@control_notification.delete("/backend/api/notification/{notification_id}")
async def update_notification(notification_id: str, sess: Session = Depends(get_db)):
    noti = sess.query(Notification).filter(
        Notification.id_notification == notification_id).first()
    if not noti:
        raise HTTPException(status_code=404, detail="Not found")
    sess.delete(noti)
    sess.commit()
    return {"ok": True}
