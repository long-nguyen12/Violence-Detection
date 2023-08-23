from cmath import log
from decimal import Decimal
import os
from detect import YoloDetect
from fastapi import Request, Response, Body, APIRouter, File, UploadFile, Depends, WebSocket, HTTPException
from app.database.models import *
import time
from typing import Union
from tempfile import NamedTemporaryFile
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
import cv2
from app.database.schemas import *
import threading
import asyncio
from fastapi.concurrency import run_in_threadpool
from starlette.websockets import WebSocketState, WebSocketDisconnect

control_camera = APIRouter()

alert_telegram_each = 60
last_alert = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@control_camera.post("/backend/api/camera/")
async def create(camera: CameraSchema, sess: Session = Depends(get_db)):
    if not camera.camera_url:
        raise HTTPException(status_code=404, detail="Camera url not found")
    url = camera.camera_url
    print(url.isnumeric())
    if url.isnumeric():
        rtspURL = url
        url = url
    else:
        if url.startswith("http"):
            url = url[7, len(url)]
        elif url.startswith("https"):
            url = url[8, url.length]
        else:
            url = url
        rtspURL = "rtsp://" + camera.camera_username + ":" + \
            camera.camera_password + "@" + url + "/cam/realmonitor?channel=1&subtype=0"

    camera = Camera(camera_url=camera.camera_url, ws_url=rtspURL, camera_name=camera.camera_name,
                    camera_username=camera.camera_username, camera_password=camera.camera_password)
    sess.add(camera)
    sess.commit()
    sess.refresh(camera)
    return {"camera": camera}


@control_camera.get("/backend/api/camera/all")
async def get_camera(sess: Session = Depends(get_db)):
    camera = sess.query(Camera).all()
    if not camera:
        raise HTTPException(status_code=404, detail="Not found")
    return {"camera": camera}


@control_camera.get("/backend/api/camera/{camera_id}")
async def get_camera(camera_id: str, sess: Session = Depends(get_db)):
    camera = sess.query(Camera).filter(Camera.idcameras == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Not found")
    return camera


@control_camera.put("/backend/api/camera/{id}")
async def update_camera(id: str, new_camera: CameraSchema, sess: Session = Depends(get_db)):
    camera = sess.query(Camera).filter(Camera.idcameras == id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Not found")

    url = camera.camera_url
    if url.isnumeric():
        rtspURL = url
    else:
        if url.startswith("http"):
            url = url[7, len(url)]
        elif url.startswith("https"):
            url = url[8, url.length]
        else:
            url = url
        rtspURL = "rtsp://" + camera.camera_username + ":" + \
            camera.camera_password + "@" + url + "/cam/realmonitor?channel=1&subtype=0"

    camera_ = new_camera.dict(exclude_unset=True)

    for key, value in camera_.items():
        setattr(camera, key, value)
    camera.ws_url = rtspURL
    sess.add(camera)
    sess.commit()
    sess.refresh(camera)
    return camera


@control_camera.websocket("/ws/{id}")
async def stream_camera(id: str, websocket: WebSocket, sess: Session = Depends(get_db)):
    camera = sess.query(Camera).filter(Camera.idcameras == id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Not found")
    url = camera.ws_url
    if url.isnumeric():
        url = int(url)
    cap = cv2.VideoCapture(url)
    await websocket.accept()

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                await websocket.send_bytes(buffer.tobytes())
                data = await run_in_threadpool(lambda: websocket.receive_text())
                if data == "DISCONNECT":
                    break
    except WebSocketDisconnect:
        print("Client disconnected")
        pass
    except Exception as e:
        print(e)
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
