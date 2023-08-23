from detect import YoloDetect
import cv2

if __name__ == '__main__':
    _model = YoloDetect()
    cap = cv2.VideoCapture(
        'D:/Work/Violence-Detection/public/files/WIN_20221203_07_48_57_Pro.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (w, h)
    result = cv2.VideoWriter('D:/Work/Violence-Detection/public/files/det_WIN_20221203_07_48_57_Pro.mov',
                             cv2.VideoWriter_fourcc(*'mp4v'),
                             fps, size)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame, attr = _model.detect_image(frame)
        result.write(frame)
