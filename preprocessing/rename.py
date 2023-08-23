import cv2
import numpy as np
import os
import glob
import time
import shutil

class Constants():
    IMAGE_FILES = 'D:/Work/datasets/datasets/images/NoViolence/train'

if __name__ == "__main__":
    constants = Constants()
    vid_path = "D:/Work/datasets/datasets/images/NoViolence/train"
    
    annotations = glob.glob(vid_path + '/image*.txt')
    
    count_anno = 0
    
    while(True):
        with open(annotations[count_anno], "r+") as f:
            old = f.read() # read everything in the file
            if not old:
                print(annotations[count_anno])
            else:
                new = '0 ' + old[1:]  
                f.seek(0) # rewind
                f.write(new) # write the new line before
            
        count_anno += 1
        if count_anno == len(annotations) - 1:
            break

# python detect_video.py --weights weights/best_1.pt --conf 0.75 --img-size 640 --source D:/Work/datasets/new_dataset/WIN_20221212_14_52_53_Pro.mp4