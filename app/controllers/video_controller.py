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


class DetectionTask(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.model = YoloDetect()
        self.url = url

    def run(self, *args, **kwargs, ):
        cap = cv2.VideoCapture(self.url)
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break
                else:
                    img, _ = self.model.detect_image(frame)
        except Exception as e:
            print(e)
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()

@control_video.post("/backend/api/video")
async def create(file: Union[UploadFile, None] = None, sess: Session = Depends(get_db)):
    print(file)
    if not file:
        raise HTTPException(status_code=404, detail="Video not found")
    elif not file.filename.lower().endswith(('.mp4')):
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

            video = Video(
                image_path=file.filename, video_path=file.filename, create_at=iso_date)
            sess.add(video)
            sess.commit()
            sess.refresh(video)
            return {"video": video}
        except:
            raise HTTPException(status_code=500)


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
                # t = DetectionTask(frame)
                # frame = t.run()
                # frame, _ = model.detect_image(frame)
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