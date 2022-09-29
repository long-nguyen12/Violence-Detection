import cv2
import numpy as np
import os
import glob
from app.constants import constants
import time

def convert2images(vid_path):
    if not os.path.exists(constants.IMAGE_FILES):
        os.makedirs(constants.IMAGE_FILES)

    videos = glob.glob(vid_path + '/*.mp4')
    for filename in videos:
        try:
            vid = cv2.VideoCapture(filename)
            count = 0
            success = True
            while success:
                try:
                    success, image = vid.read()
                    ts = time.time()
                    img_path = os.path.join(
                        constants.IMAGE_FILES, "image%d.jpg" % int(ts * 1000)).replace("\\", "/")
                    cv2.imwrite(img_path, image)
                except Exception as e:
                    print(e)
            cv2.destroyAllWindows()
        except Exception as e:
            print(e)
        
        
if __name__ == "__main__":
    convert2images('./datasets/Vat_nhau_danh_nhau')