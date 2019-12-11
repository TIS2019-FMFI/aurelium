"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.

stopne sa kratky act a ulozi sa
potom pobezi dalsi kratky act ale pokracuje aj ten dlhy
kratke sa zatial zapisuju do pola
ked skonci dlhy tak sa spytam ci je rovnaky jak ktatky a ci medzi nimi nebola medzera na dalsi ukon
ak hej tak sa zapise dlhy, ak nie yapisu sa kratke z pola

"""

import cv2
import time

from gaze_tracking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
window_name = "Demo"
#cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

current_gesture = ""
gesture_end_duration = 3
short_act_duration = 1
long_act_duration = 2

acts = {'l': 0, 'r': 0, 'b': 0, '_': 0}
act_started = False
gesture_started = False
act_start_time = time.time()
act_stop_time = time.time()
gestureEnd_start_time = time.time()
gestureEnd_stop_time = time.time()
detection_of_end = False
        
def detect():
    global current_gesture
    global long
    
    print(acts)
    max_act = "_"
    for key in acts:
        if acts[key] > acts[max_act]:
            max_act = key
    for key in acts:
        acts[key] = 0
    current_gesture += max_act
    
    print_act(max_act)


def print_act(act):
    if act == 'l':
        print('left closed')
    if act == 'r':
        print('right closed')
    if act == 'b':
        print('both closed')
    if act == '_':
        print('none closed')
        

def detect_end():
    global gesture_started
    global current_gesture
    #print('detekujem koniec')
    if time.time() > gestureEnd_end_time:
        gesture_started = False
        print(current_gesture)
        current_gesture = ""

while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""

    rightClosed = gaze.is_closeRight()
    leftClosed = gaze.is_closeLeft()

    if (gesture_started == False and (rightClosed or leftClosed)):
        gesture_started = True
        
    if (act_started == False and (rightClosed or leftClosed)):
        act_started = True
        print('started')
        act_start_time = time.time()
        act_stop_time = act_start_time + short_act_duration

    if act_started == True:
        if time.time() > act_stop_time:
            detect()
            act_started = False
        

    if rightClosed and leftClosed:   
        #text = "Closed both"
        detection_of_end = False
        if act_started == True:
            acts["b"] += 1 
    elif rightClosed:
        #text = "Closed left"
        detection_of_end = False
        if act_started == True:
            acts["l"] += 1
    elif leftClosed:
        #text = "Closed right"
        detection_of_end = False
        if act_started == True:
            acts["r"] += 1
    else:
        if act_started == True:
            acts["_"] += 1

    if gesture_started == True and detection_of_end == False:
        detection_of_end = True
        gestureEnd_start_time = time.time()
        gestureEnd_end_time = gestureEnd_start_time + gesture_end_duration
    if gesture_started == True and detection_of_end == True:
        detect_end()

            
    #if gaze.is_blinking():
        #text = "Blinking"


    
    '''  
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"
    '''
    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    cv2.imshow("Demo", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    #if cv2.waitKey(1) == 27:
        #break


cv2.destroyAllWindows()
