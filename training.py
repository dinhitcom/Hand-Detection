import dlib
import glob
import cv2
import os
import shutil
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import pyautogui as pyg
from params import *


def display_samples(samples_num, data):
    np.random.shuffle(data)
    cols = 5
    rows = int(np.ceil(samples_num / cols))
    plt.figure(figsize=(cols * cols, rows * cols))

    for i in range(samples_num):
        d_box = data[i][1][0]
        left, top, right, bottom = d_box.left(), d_box.top(), d_box.right(), d_box.bottom()
        image = data[i][0]
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        plt.subplot(rows, cols, i + 1)
        plt.imshow(image[:, :, ::-1])
        plt.axis('off')

def preprocessing(save_directory, box_info_file):
    data = {}
    image_names = os.listdir(save_directory)
    image_indexes = [int(img_name.split('.')[0]) for img_name in image_names]
    np.random.shuffle(image_indexes)
    file_reader = open(box_info_file, 'r')
    box_info = file_reader.read()
    box_info_dict = eval('{' + box_info + '}')
    file_reader.close()

    for index in image_indexes:
        img = cv2.imread(os.path.join(save_directory, str(index) + '.png'))
        bounding_box = box_info_dict[index]
        x1, y1, x2, y2 = bounding_box
        dlib_box = [dlib.rectangle(left=x1, top=y1, right=x2, bottom=y2)]
        data[index] = (img, dlib_box)

    print('Number of Images and Boxes Present: {}'.format(len(data)))
    return data


def train_data(data, model_file, train_rate=1, horizontal_flip=False, C=5, metrics=True, save_to_file=True):
    train_num = int(len(data) * train_rate)
    images = [tuple_value[0] for tuple_value in data.values()]
    bounding_boxes = [tuple_value[1] for tuple_value in data.values()]
    options = dlib.simple_object_detector_training_options()
    options.add_left_right_image_flips = horizontal_flip
    options.C = C
    options.num_threads = 4
    start_time = time.time()
    print('Start training')
    detector = dlib.train_simple_object_detector(images[:train_num], bounding_boxes[:train_num], options)
    print('Training completed, taken: {:.2f} seconds'.format(time.time() - start_time))

    if save_to_file:
        detector.save(model_file)

    if metrics:
        win_det = dlib.image_window()
        win_det.set_image(detector)
        if train_rate < 1:
            print("Training Metrics: {}".format(dlib.test_simple_object_detector(images[:train_num], bounding_boxes[:train_num], detector)))
            print("Testing Metrics: {}".format(dlib.test_simple_object_detector(images[train_num:], bounding_boxes[train_num:], detector)))
        else:
            print("Training Metrics: {}".format(dlib.test_simple_object_detector(images, bounding_boxes, detector)))
    return detector, images


data = preprocessing('dataset/lefthand', 'lefthand_box_info.txt')
detector, images = train_data(data, 'lefthand_detector.svm', horizontal_flip=False, C=5, metrics=False, save_to_file=True)
