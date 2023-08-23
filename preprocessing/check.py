import cv2
import numpy as np
import os
import glob
import time
import shutil

class Constants():
    IMAGE_FILES = 'D:/Work/actions/actions/Duoi_nhau/imgs'
    SOURCE = 'D:/Work/actions/actions/Duoi_nhau'

if __name__ == "__main__":
    constants = Constants()
    vid_path = "D:/Work/actions/actions/Duoi_nhau"
    
    images = glob.glob('D:/Work/ds_actions/train/images' + '/image*.jpg')
    annotations = glob.glob('D:/Work/ds_actions/train/labels' + '/image*.txt')
    
    count_img = 0
    count_anno = 0
    
    while(True):
        image_name = images[count_img].split('.')[0]
        anno_name = annotations[count_anno].split('.')[0]
        print(image_name == anno_name)
        # if image_name == anno_name:
        #     count_anno += 1
        # else: print(image_name, anno_name)
        count_anno += 1
        count_img += 1
        if count_img == len(images) - 1:
            break