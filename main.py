import os
import threading
from app.constants import Constants
from app.controllers import camera_controller, notification_controller, auth_controller
from detect import YoloDetect
from fastapi import FastAPI, Depends
import uvicorn
from app.database.database import engine, SessionLocal
from app.database import models
from fastapi.staticfiles import StaticFiles
import cv2
models.Base.metadata.create_all(bind=engine)


app = FastAPI()
if not os.path.exists(Constants.PUBLIC_FOLDER):
    os.makedirs(Constants.PUBLIC_FOLDER)
app.mount("/static", StaticFiles(directory=Constants.PUBLIC_FOLDER), name="static")


@app.get("/")
def root():
    return {
        "message": ""
    }


app.include_router(camera_controller.control_camera)
app.include_router(notification_controller.control_notification)
app.include_router(auth_controller.control_auth)


class DetectionTask(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.model = YoloDetect()

    def run(self, *args, **kwargs, ):
        # cap = cv2.VideoCapture(
        #     'rtsp://admin:Admin12345@tronghau7.kbvision.tv:37779/cam/realmonitor?channel=1&subtype=0', cv2.CAP_FFMPEG)
        cap = cv2.VideoCapture('D:/Work/datasets/_datasets/Vat_nhau_danh_nhau/2881825290563252032.mp4')
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


# @app.on_event("startup")
# async def startup_event():
#     t = DetectionTask()
#     t.start()

if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)
