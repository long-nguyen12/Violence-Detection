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
from app.constants import *
import threading
import asyncio
import aiofiles
from fastapi.concurrency import run_in_threadpool
from starlette.websockets import WebSocketState, WebSocketDisconnect
from pathlib import Path
import time
from fastapi.responses import StreamingResponse, FileResponse

control_video = APIRouter()

alert_telegram_each = 60
last_alert = None

SUB_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()
PARENT_PATH = SUB_PATH.parent.absolute()

from pathlib import Path
from app.constants import *
import aiofiles
from fastapi_pagination import Page, add_pagination, paginate, Params
import ctypes

import threading
from fastapi.concurrency import run_in_threadpool

from detect import YoloDetect
control_video = APIRouter()

SUB_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()
PARENT_PATH = SUB_PATH.parent.absolute()

model = YoloDetect()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


model = YoloDetect()


class DetectionTask(threading.Thread):
    def __init__(self, model, filename, path, save_path, det_filename):
        threading.Thread.__init__(self)
        self.model = model
        self.filename = filename
        self.path = path
        self.save_path = save_path
        self.det_filename = det_filename
        self.result = None

    def run(self):
        attr = None
        if self.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            img = cv2.imread(self.path)
            try:
                img, attr = self.model.detect_photo(img)
                cv2.imwrite(self.save_path, img)
            except Exception as e:
                print(e)
        else:
            cap = cv2.VideoCapture(self.path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            size = (w, h)
            self.save_path = self.save_path.replace('.mp4', '.mov')
            self.det_filename = self.det_filename.replace('.mp4', '.mov')
            result = cv2.VideoWriter(self.save_path,
                                     cv2.VideoWriter_fourcc(*'mp4v'),
                                     fps, size)
            try:
                while True:
                    success, frame = cap.read()
                    if not success:
                        break
                    else:
                        try:
                            res, attr = self.model.detect_image(frame)
                        except Exception as e:
                            print(e)
                        result.write(res)
            except Exception as e:
                print(e)
            finally:
                cv2.destroyAllWindows()
        self.result = (self.det_filename, attr)

    def get_result(self):
        return self.result[0], self.result[1]


@control_video.post("/backend/api/videos/")
async def create(file: Union[UploadFile, None] = None, sess: Session = Depends(get_db)):
    if not file:
        raise HTTPException(status_code=404, detail="Image not found")
    elif not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.mp4', '.mov')):
        raise HTTPException(status_code=401, detail="Wrong format")
    else:
        file_copy = os.path.join(
            PARENT_PATH, Constants.PUBLIC_FOLDER + file.filename)
        try:
            async with aiofiles.open(file_copy, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)

            timestamp = int(time.time())
            det_filename = str(timestamp) + "_" + file.filename
            save_path = os.path.join(
                PARENT_PATH, Constants.PUBLIC_FOLDER + det_filename)

            detection_thread = DetectionTask(
                model, file.filename, file_copy, save_path, det_filename)
            detection_thread.start()
            detection_thread.join()
            res, attrs = detection_thread.get_result()
            
            if res:
                if det_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    now = datetime.now()
                    iso_date = now.isoformat()
                    noti = Notification(
                        image=res, create_at=iso_date, confirmed=0)
                    sess.add(noti)
                    sess.commit()
                    sess.refresh(noti)
                else:
                    for det in attrs:
                        noti = Notification(
                            image=det['img'], create_at=det['time'], confirmed=0)
                        sess.add(noti)
                        sess.commit()
                        sess.refresh(noti)

            return {"path": res, 'detection': attrs}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500)

@control_video.get("/backend/api/videos/all")
async def get_camera(sess: Session = Depends(get_db)):
    camera = sess.query(Camera).all()
    if not camera:
        raise HTTPException(status_code=404, detail="Not found")
    return {"camera": camera}


@control_video.get("/backend/api/videos/{video_name}")
async def download_file(video_name: str):
    save_path = os.path.join(
        PARENT_PATH, Constants.DETECTION_FOLDER + video_name)
    return FileResponse(save_path, media_type="video/mp4", filename=video_name)


@control_video.get("/backend/api/video/all", response_model=Page[VideoSchema])
async def get_videos(params: Params = Depends(), sess: Session = Depends(get_db)):
    video = sess.query(Video).all()
    if not video:
        raise HTTPException(status_code=404, detail="Not found")
    video = video[::-1]
    return paginate(video, params)


@control_video.get("/backend/api/video/{video_id}")
async def update_video(video_id: str, sess: Session = Depends(get_db)):
    video = sess.query(Video).filter(
        Video.id_video == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Not found")
    return video


@control_video.delete("/backend/api/video/{video_id}")
async def update_video(video_id: str, sess: Session = Depends(get_db)):
    video = sess.query(Video).filter(
        Video.id_video == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Not found")
    sess.delete(video)
    sess.commit()
    return {"ok": True}


@control_video.websocket("/ws/video/{id}")
async def stream_video(id: str, websocket: WebSocket, sess: Session = Depends(get_db)):
    video = sess.query(Video).filter(Video.id_video == id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Not found")
    # url = os.path.join(PARENT_PATH, Constants.PUBLIC_FOLDER, video.video_path)
    url = 'D:/Coding/datasets/datasets/' + video.video_path
    t = DetectionTask(url)
    t.start()
    cap = cv2.VideoCapture(url)
    await websocket.accept()

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                # frame, _ = model.detect_image(frame)
                ret, buffer = cv2.imencode('.jpg', frame)
                await websocket.send_bytes(buffer.tobytes())
                data = await run_in_threadpool(lambda: websocket.receive_text())
                if data == "DISCONNECT":
                    t.stop()
                    t.join()
                    break
    except WebSocketDisconnect:
        print("Client disconnected")
        pass
    except Exception as e:
        print(e)
        pass
    finally:
        t.stop()
        t.join()
        cap.release()
        cv2.destroyAllWindows()