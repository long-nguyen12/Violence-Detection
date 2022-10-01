import glob
import os
import shutil
import random


def delete_unused_file():
    imgs = glob.glob("D:/Work/datasets/images/image*.jpg")
    labels = glob.glob("D:/Work/datasets/images/image*.txt")

    imgs_name = []
    labels_name = []

    for img in imgs:
        imgs_name.append(img)
    for label in labels:
        labels_name.append(label)

    count = 0
    count_img = 0
    total_label = len(labels)
    while count < total_label:
        label = labels_name[count]
        label = label.replace("\\", "/")
        label_file = label.split('/')[-1]
        label_file_name = label_file.split('.')[0]

        img = imgs_name[count_img]
        img = img.replace("\\", "/")
        img_file = img.split('/')[-1]
        img_file_name = img_file.split('.')[0]

        if label_file_name == img_file_name:
            count += 1
        else:
            os.remove(img)

        count_img += 1
    print("Done!")


def split_images():
    imgs = glob.glob("D:/Work/datasets/images/image*.jpg")
    labels = glob.glob("D:/Work/datasets/images/image*.txt")

    FOLDER_1 = "D:/Work/datasets/Da_nhau/"
    FOLDER_2 = "D:/Work/datasets/Dam_nhau/"
    FOLDER_3 = "D:/Work/datasets/Duoi_nhau/"
    FOLDER_4 = "D:/Work/datasets/Vat_nhau/"

    count = 0
    total_label = len(labels)

    while count < total_label:
        label = labels[count]
        img = imgs[count]

        f = open(label, "r")
        class_name = f.readline()
        class_index = class_name.strip()[0]
        if int(class_index) == 0:
            shutil.copy2(img, FOLDER_1)
            shutil.copy2(label, FOLDER_1)
        elif int(class_index) == 1:
            shutil.copy2(img, FOLDER_2)
            shutil.copy2(label, FOLDER_2)
        elif int(class_index) == 2:
            shutil.copy2(img, FOLDER_3)
            shutil.copy2(label, FOLDER_3)
        else:
            shutil.copy2(img, FOLDER_4)
            shutil.copy2(label, FOLDER_4)
        count += 1

    print(count)


def move_images():
    BASE_FOLDER = "D:/Work/datasets/train_data"
    train_imgs = glob.glob(BASE_FOLDER + "/train/image*.jpg")
    train_labels = glob.glob(BASE_FOLDER + "/train/image*.txt")
    val_imgs = glob.glob(BASE_FOLDER + "/val/image*.jpg")
    val_labels = glob.glob(BASE_FOLDER + "/val/image*.txt")

    TRAIN_IMG = "D:/Work/datasets/train_data/train/images"
    TRAIN_LABEL = "D:/Work/datasets/train_data/train/labels"
    VAL_IMG = "D:/Work/datasets/train_data/val/images"
    VAL_LABEL = "D:/Work/datasets/train_data/val/labels"

    if not os.path.exists(TRAIN_IMG):
        os.makedirs(TRAIN_IMG)
    if not os.path.exists(TRAIN_LABEL):
        os.makedirs(TRAIN_LABEL)
    if not os.path.exists(VAL_IMG):
        os.makedirs(VAL_IMG)
    if not os.path.exists(VAL_LABEL):
        os.makedirs(VAL_LABEL)

    count_train = 0
    total_train_label = len(train_labels)

    while count_train < total_train_label:
        label = train_labels[count_train]
        img = train_imgs[count_train]
        print(label, img)
        shutil.move(img, TRAIN_IMG)
        shutil.move(label, TRAIN_LABEL)

        count_train += 1
    print(count_train)
    
    count_val = 0
    total_val_label = len(val_labels)

    while count_val < total_val_label:
        label = val_labels[count_val]
        img = val_imgs[count_val]
        print(label, img)
        shutil.move(img, VAL_IMG)
        shutil.move(label, VAL_LABEL)

        count_val += 1

    print(count_val)


def split_dataset(is_subfolder=False):
    TRAIN_FOLDER = "D:/Work/datasets/train_data/train/"
    VAL_FOLDER = "D:/Work/datasets/train_data/val/"

    if not os.path.exists(TRAIN_FOLDER):
        os.makedirs(TRAIN_FOLDER)
    if not os.path.exists(VAL_FOLDER):
        os.makedirs(VAL_FOLDER)

    ratio = 0.8

    def move(paths, folder):
        for p in paths:
            shutil.move(p, folder)

    if is_subfolder:
        BASE_FOLDER = 'D:/Work/datasets/origin_data'
        os.chdir(BASE_FOLDER)
        all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]

        for dir_name in all_subdirs:
            dir = os.path.join(BASE_FOLDER, dir_name)
            img_paths = glob.glob(dir + "/image*.jpg")
            txt_paths = glob.glob(dir + "/image*.txt")

            data_size = len(img_paths)
            train_size = int(data_size * ratio)

            img_txt = list(zip(img_paths, txt_paths))
            random.seed(43)
            random.shuffle(img_txt)
            img_paths, txt_paths = zip(*img_txt)
            # Now split them
            train_img_paths = img_paths[:train_size]
            train_txt_paths = txt_paths[:train_size]

            valid_img_paths = img_paths[train_size:]
            valid_txt_paths = txt_paths[train_size:]

            move(train_img_paths, TRAIN_FOLDER)
            move(train_txt_paths, TRAIN_FOLDER)
            move(valid_img_paths, VAL_FOLDER)
            move(valid_txt_paths, VAL_FOLDER)
    else:
        BASE_FOLDER = 'D:/Work/datasets/images_one_label'

        img_paths = glob.glob(BASE_FOLDER + "/image*.jpg")
        txt_paths = glob.glob(BASE_FOLDER + "/image*.txt")

        data_size = len(img_paths)
        train_size = int(data_size * ratio)

        img_txt = list(zip(img_paths, txt_paths))
        random.seed(43)
        random.shuffle(img_txt)
        img_paths, txt_paths = zip(*img_txt)
        # Now split them
        train_img_paths = img_paths[:train_size]
        train_txt_paths = txt_paths[:train_size]

        valid_img_paths = img_paths[train_size:]
        valid_txt_paths = txt_paths[train_size:]

        move(train_img_paths, TRAIN_FOLDER)
        move(train_txt_paths, TRAIN_FOLDER)
        move(valid_img_paths, VAL_FOLDER)
        move(valid_txt_paths, VAL_FOLDER)


def convert_class_type():
    LABEL_PATH = "D:/Work/datasets/images_one_label"

    labels = glob.glob(LABEL_PATH + "/image*.txt")

    for label_file in labels:
        f = open(label_file, "r+")
        class_name = f.readline()

        class_name = class_name.strip()
        class_name = str(0) + class_name[1: len(class_name)]

        # write file
        f.seek(0)
        f.write(class_name)


if __name__ == "__main__":
    # split_dataset(is_subfolder=False)
    # convert_class_type()
    move_images()
