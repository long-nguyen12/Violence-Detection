import cv2
import numpy as np
import os
import glob
import time

class Constants():
    IMAGE_FILES = 'actions/Vat_nhau/'

constants = Constants()

def convert2images(vid_path):
    if not os.path.exists(constants.IMAGE_FILES):
        os.makedirs(constants.IMAGE_FILES)

    videos = glob.glob(vid_path + '/*.mp4')
    for filename in videos:
        try:
            vid = cv2.VideoCapture(filename)
            success = True
            count = 0
            while success:
                try:
                    count += 1
                    success, image = vid.read()
                    if count % 5 == 0:
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
    convert2images('D:\Work\datasets\Du lieu camera moi\Cac hanh dong bao luc\Vat nhau danh nhau nu_nu')