import cv2
import os
import time
import utils
# from params import *

def capture(save_directory, box_info_file, cleanup=False):
    cv2.namedWindow('Capture', cv2.WINDOW_AUTOSIZE)
    # cv2.setWindowProperty("Capture",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    # cv2.resizeWindow('Capture', 640, 480)
    cv2.moveWindow('Capture', 0, 0)
    cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
    # cap = cv2.VideoCapture('http://192.168.1.2:4747/mpjpegfeed')
    x1, y1 = 0, 0
    x_step, y_step = 6, 80
    window_width = 240
    window_height = 240
    skip_frames = 3
    frame_gap = 0
    counter = 0

    if cleanup:
        utils.clean_if_exists(save_directory)
        open(box_info_file, 'w').close()
        counter = 0

    elif os.path.exists(box_info_file):
        with open(box_info_file, 'r') as f:
            box_info = f.read()

        counter = int(box_info.split(':')[-2].split(',')[-1])

    file_stream = open(box_info_file, 'a')
    utils.mkdir_if_not_exists(save_directory)
    initial_wait = 0

    while True:
        success, frame = cap.read()
        # print(frame.shape)
        if not success:
            break

        frame = cv2.flip(frame, 1)
        original_frame = frame.copy()

        if initial_wait > 60:
            frame_gap += 1

            if x1 + window_width < frame.shape[1]:
                x1 += x_step
                time.sleep(0.1)

            elif y1 + window_height + 270 < frame.shape[1]:
                y1 += y_step
                x1 = 0
                frame_gap = 0
                initial_wait = 0
            else:
                break
        else:
            initial_wait += 1

        if frame_gap == skip_frames:
            img_name = str(counter) + '.png'
            img_path = os.path.join(save_directory, img_name)
            cv2.imwrite(img_path, original_frame)
            file_stream.write('{}:({},{},{},{}),'.format(counter, x1, y1, x1 + window_width, y1 + window_height))
            counter += 1
            frame_gap = 0

        cv2.rectangle(frame, (x1, y1), (x1 + window_width, y1 + window_height), (0, 255, 0), 2)
        cv2.imshow('Capture', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyWindow('Capture')
    file_stream.close()
    return 0

capture('dataset/lefthand', 'lefthand_box_info.txt', cleanup=False)