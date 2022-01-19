import dlib
import cv2
import time

model_file = 'lefthand_detector4.svm'
# model_file = 'Hand_Detector.svm'
detector = dlib.simple_object_detector(model_file)
cv2.namedWindow('Hand Detection', cv2.WINDOW_AUTOSIZE)
# cv2.resizeWindow('Hand Detection', 1920, 1080)
cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
scale_factor = 2
size, center_x, center_y = 0, 0, 0
fps = 0
frame_counter = 0
start_time = time.time()
size_up_thres = 80000
size_down_thres = 45000
top_thres = 240
bottom_thres = 480
left_thres = 320
right_thres = 640
text = 'No Hand Detected'
is_key_down = False
is_key_up = False

while True:
    success, frame = cap.read()
    # print(frame.shape)
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame_counter += 1
    fps = (frame_counter / (time.time() - start_time))
    original_frame = frame.copy()
    resized_width = int(frame.shape[1]/scale_factor)
    resized_height = int(frame.shape[0]/scale_factor)
    resized_frame = cv2.resize(original_frame, (resized_width, resized_height))
    dectections = detector(resized_frame)

    for detection in dectections:
        x1 = int(detection.left() * scale_factor)
        y1 = int(detection.top() * scale_factor)
        x2 = int(detection.right() * scale_factor)
        y2 = int(detection.bottom() * scale_factor)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, 'Left Hand', (x1, y2+20), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 2)
        size = int((x2 - x1) * (y2 - y1))
        center_x = int(x1 + (x2 - x1) / 2)
        center_y = int(y1 + (y2 -y1) / 2)

        if center_x < left_thres:
            if center_y < top_thres:
                text = 'Top left'
                # pyg.hotkey('A', 'W')
            elif center_y > bottom_thres:
                text = 'Bottom left'
                # pyg.hotkey('A', 'S')
            else:
                text = 'Left'
                # pyg.hotkey('A')

        elif center_x > right_thres:
            if center_y < top_thres:
                text = 'Top right'
                # pyg.hotkey('D', 'W')
            elif center_y > bottom_thres:
                text = 'Bottom right'
                # pyg.hotkey('D', 'S')

            else:
                text = 'Right'
                # pyg.hotkey('D')
        else:
            if center_y < top_thres:
                text = 'Top'
                # pyg.hotkey('W')

            elif center_y > bottom_thres:
                text = 'Bottom'
                # pyg.hotkey('S')

            else:
                text = 'Center'

        if size < size_down_thres:
            if not is_key_down:
                is_key_down = True
                is_key_up = False

        elif size > size_up_thres:
            if is_key_down and not is_key_up:
                is_key_up = True
                is_key_down = False

        if is_key_up:
            is_key_up = False

        cv2.putText(frame, 'Center: x: {}, y: {}'.format(center_x, center_y), (540, 20), cv2.FONT_HERSHEY_COMPLEX, 0.8, (233, 100, 25))
        cv2.putText(frame, 'size: {}'.format(size), (540, 40), cv2.FONT_HERSHEY_COMPLEX, 0.8, (233, 100, 25))

    cv2.putText(frame, 'FPS: {:.2f}'.format(fps), (20, 20), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255),2)
    cv2.putText(frame, text, (220, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (33, 100, 185), 2)
    cv2.imshow('Hand Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyWindow('Hand Detection')