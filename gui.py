import dlib
import cv2
import time
import pyautogui as pyg
from tkinter import *
from PIL import Image, ImageTk

model_file = 'lefthand_detector4.svm'
detector = dlib.simple_object_detector(model_file)
scale_factor = 2.5
size, center_x, center_y = 0, 0, 0
fps = 0
frame_counter = 0
start_time = time.time()
size_up_thres = 80000
size_down_thres = 50000
top_thres = 240
bottom_thres = 480
left_thres = 320
right_thres = 640
text = 'No Hand Detected'
is_key_down = False
is_key_up = False
key = -1
control_type = 'WASD'
require_key_press = False
center_button = 'none'
key_list = [['A', 'W'], 'W', ['D', 'W'], 'A', center_button, 'D', ['A', 'S'], 'S', ['D', 'S']]
is_start = False

root = Tk()
root.wm_title('Hand Control')
root.config(background="#FFFFFF")
root.geometry('1380x740+0+0')
imageFrame = Frame(root, width=960, height=720)
imageFrame.grid(row=0, column=0, rowspan=20, padx=5, pady=5)
lmain = Label(imageFrame)
lmain.grid(row=0, column=0, rowspan=20)

control_type_label = Label(root, text='Control type: ', font=('Helvetica', 11))
control_type_label.grid(row=0, column=1, padx=11, sticky=W)
control_type_var = StringVar(root, control_type)
control_type_list = ['WASD', 'Arrow Key']

def set_control_type(type):
    global key_list, control_type

    if type == control_type_list[0]:
        key_list = [['A', 'W'], 'W', ['D', 'W'], 'A', center_button, 'D', ['A', 'S'], 'S', ['D', 'S']]
    elif type == control_type_list[1]:
        key_list = [['left', 'up'], 'up', ['right', 'up'], 'left', center_button, 'right', ['left', 'down'], 'down', ['right', 'down']]
    # print(key_list)
    control_type = type

    return 0

control_type_select = OptionMenu(root, control_type_var, *control_type_list, command=set_control_type)
control_type_select.configure(background='white', activebackground='white', font=('Helvetica', 11), relief='groove', width='15')
control_type_select["menu"].configure(bg="white")
control_type_select.grid(row=0, column=2, sticky=W)

mode_label = Label(root, text='Select mode: ', font=('Helvetica', 11))
mode_label.grid(row=1, column=1, padx=10, sticky=W)
mode_var = StringVar(root, 'Game Movement')
mode_list = ['Game Movement', 'Key Control']

def set_mode(mode):
    global require_key_press

    if mode == mode_list[0]:
        require_key_press = False
    else:
        require_key_press = True

    return 0

mode_select = OptionMenu(root, mode_var, *mode_list, command=set_mode)
mode_select.configure(background='white', activebackground='white', font=('Helvetica', 11), relief='groove', width='15')
mode_select["menu"].configure(bg="white")
mode_select.grid(row=1, column=2, sticky=W)

center_button_label = Label(root, text='Center button: ', font=('Helvetica', 11))
center_button_label.grid(row=2, column=1, padx=10, sticky=W)
center_button_var = StringVar(root, 'none')
center_key_list = ['none', 'space', 'enter', 'esc', 'shift', 'backspace']

def set_center_button(key):
    global center_button, key_list

    center_button = key
    key_list[4] = key
    # print(key_list)

    return 0

center_button_select = OptionMenu(root, center_button_var, *center_key_list, command=set_center_button)
center_button_select.configure(background='white', activebackground='white', font=('Helvetica', 11), relief='groove', width='15')
center_button_select["menu"].configure(bg="white")
center_button_select.grid(row=2, column=2,  sticky=W)

up_thres_label = Label(root, text='Key up threshold: ', font=('Helvetica', 11))
up_thres_label.grid(row=3, column=1, sticky=W, padx=10)
up_thres_var = IntVar(root, value=size_up_thres)
up_thres_entry = Entry(root, textvariable=up_thres_var, font=('Helvetica', 13), width=15)
up_thres_entry.grid(row=3, column=2, sticky=W)

down_thres_label = Label(root, text='Key down threshold: ', font=('Helvetica', 11))
down_thres_label.grid(row=4, column=1, sticky=W, padx=10)
down_thres_var = IntVar(root, value=size_down_thres)
down_thres_entry = Entry(root, textvariable=down_thres_var, font=('Helvetica', 13), width=15)
down_thres_entry.grid(row=4, column=2, sticky=W)

def start_control(up_thres_var, down_thres_var):
    global is_start, size_up_thres, size_down_thres

    is_start = True
    up_thres = up_thres_var.get()
    down_thres = down_thres_var.get()

    if type(up_thres) is int and type(down_thres) is int:
        if up_thres > down_thres:
            size_down_thres = down_thres
            size_up_thres = up_thres

            return 0

    return -1

start_button = Button(root, text='Start', font=('Helvetica', 11), width=15, command=lambda: start_control(up_thres_var, down_thres_var))
start_button.grid(row=5, column=1, sticky=W, padx=10)

def stop_control():
    global is_start
    is_start = False

stop_button = Button(root, text='Stop', font=('Helvetica', 11), width=15, command=lambda: stop_control())
stop_button.grid(row=5, column=2, sticky=W, padx=10)
cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)

is_key_release = True
key_down_list = []
current_key_down = None

def show_frame():
    global detector
    global scale_factor, size, center_x, center_y, fps, frame_counter, start_time
    global size_up_thres, size_down_thres, top_thres, bottom_thres, left_thres, right_thres
    global text, is_key_up, is_key_down, key, is_key_release, key_down_list, current_key_down

    success, frame = cap.read()

    if not success:
        return -1

    frame = cv2.flip(frame, 1)
    frame_counter += 1
    # fps = (frame_counter / (time.time() - start_time))
    original_frame = frame.copy()
    resized_width = int(frame.shape[1] / scale_factor)
    resized_height = int(frame.shape[0] / scale_factor)
    resized_frame = cv2.resize(original_frame, (resized_width, resized_height))
    dectections = detector(resized_frame)
    hand_found = False
    for detection in dectections:
        if not hand_found:
            hand_found = True
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
                key = 0
                # pyg.hotkey('A', 'W')
            elif center_y > bottom_thres:
                text = 'Bottom left'
                key = 6
                # pyg.hotkey('A', 'S')
            else:
                text = 'Left'
                key = 3
                # pyg.hotkey('A')

        elif center_x > right_thres:
            if center_y < top_thres:
                text = 'Top right'
                key = 2
                # pyg.hotkey('D', 'W')
            elif center_y > bottom_thres:
                text = 'Bottom right'
                key = 8
                # pyg.hotkey('D', 'S')

            else:
                text = 'Right'
                key = 5
                # pyg.hotkey('D')
        else:
            if center_y < top_thres:
                text = 'Top'
                key = 1
                # pyg.hotkey('W')

            elif center_y > bottom_thres:
                text = 'Bottom'
                key = 7
                # pyg.hotkey('S')

            else:
                text = 'Center'
                key = 4

        if size < size_down_thres:
            if not is_key_down:
                is_key_down = True
                is_key_up = False

        elif size > size_up_thres:
            if is_key_down and not is_key_up:
                is_key_up = True
                is_key_down = False

        if is_start:
            if not require_key_press:
                if key != 4:
                    # print(current_key_down)
                    if not current_key_down:
                        current_key_down = key
                    elif key != current_key_down:
                        if type(key_list[current_key_down]) is list:
                            pyg.keyUp(key_list[current_key_down][0])
                            pyg.keyUp(key_list[current_key_down][1])
                        else:
                            pyg.keyUp(key_list[current_key_down])

                        print(key_list[current_key_down], ' key up')
                        current_key_down = key
                        is_key_release = True
                    if is_key_release:
                        if type(key_list[key]) is list:
                            pyg.keyDown(key_list[key][0])
                            pyg.keyDown(key_list[key][1])
                        else:
                            pyg.keyDown(key_list[key])

                        print(key_list[current_key_down], ' key down')
                        is_key_release = False

                    # if not is_key_release:
                    #     print(key_down_list)
                    #     for key_down in key_down_list:
                    #         if key_down != key:
                    #             if type(key_list[key_down]) is list:
                    #                 # pyg.hotkey(key_list[key][0], key_list[key][1])
                    #                 pyg.keyUp(key_list[key_down][0])
                    #                 pyg.keyUp(key_list[key_down][1])
                    #             else:
                    #                 # pyg.hotkey(key_list[key])
                    #                 pyg.keyUp(key_list[key_down])
                    # if key not in key_down_list:
                    #     key_down_list.append(key)

                    # if type(key_list[key]) is list:
                    #     pyg.hotkey(key_list[key][0], key_list[key][1])
                    #     # pyg.keyDown(key_list[key][0])
                    #     # pyg.keyDown(key_list[key][1])
                    #     # is_key_release = False
                    # else:
                    #     pyg.hotkey(key_list[key])
                    #     # pyg.keyDown(key_list[key])
                    #     # is_key_release = False
                    # # print(key_list[key], ' is pressed')
                else:
                    if is_key_up:
                        pyg.press(key_list[key])
                        is_key_up = False
            else:
                if is_key_up:
                    if type(key_list[key]) is list:
                        pyg.hotkey(key_list[key][0], key_list[key][1])
                    else:
                        pyg.hotkey(key_list[key])
                    is_key_up = False

        cv2.putText(frame, 'Center: x: {}, y: {}'.format(center_x, center_y), (540, 20), cv2.FONT_HERSHEY_COMPLEX, 0.8, (233, 100, 25))
        cv2.putText(frame, 'size: {}'.format(size), (540, 40), cv2.FONT_HERSHEY_COMPLEX, 0.8, (233, 100, 25))

    fps = (frame_counter / (time.time() - start_time))
    frame_counter = 0
    start_time = time.time()
    cv2.putText(frame, 'FPS: {:.2f}'.format(fps), (20, 20), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(frame, text, (220, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (33, 100, 185), 2)
    if not hand_found and not is_key_release:
        if type(key_list[current_key_down]) is list:
            pyg.keyUp(key_list[current_key_down][0])
            pyg.keyUp(key_list[current_key_down][1])
        else:
            pyg.keyUp(key_list[current_key_down])
        is_key_release = True
        print(key_list[current_key_down], ' key up')
        current_key_down = None
        # for key_down in key_down_list:
        #     print('release ', key_down_list)
        #     if type(key_list[key_down]) is list:
        #         pyg.hotkey(key_list[key][0], key_list[key][1])
                # pyg.keyUp(key_list[key_down][0])
                # pyg.keyUp(key_list[key_down][1])
            # else:
            #     pyg.hotkey(key_list[key])
                # pyg.keyUp(key_list[key_down])
            # print(key_list[key], ' is up')
        key = -1
        # key_down_list = []
        # is_key_release = True
    # print(key)
    text = 'No Hand Detected'
    output_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(output_img)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)

    lmain.after(1, show_frame)

show_frame()
root.mainloop()