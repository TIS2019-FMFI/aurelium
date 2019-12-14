"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
import time

from gaze_tracking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
window_name = "Demo"
#cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
gesture_end_duration = 3
short_act_duration = 1
long_act_duration = 2
current_gesture = ""

act_started = False
acts = []
act_start_time = time.time()
act_stop_time = time.time()
gesture_started = False
gestureEnd_start_time = time.time()
gestureEnd_stop_time = time.time()
detection_of_end = False

listBlop = {"Closed left":0,"Closed right":0,"Nothing":0}
counter = 0
text = ""

def start_act():
    global act_started
    global act_start_time
    if act_started == False:
        act_started = True
        print('act started')
        act_start_time = time.time()

def detect_end():
    global gesture_started
    global current_gesture
    global detection_of_end
    if time.time() > gestureEnd_end_time:
        gesture_started = False
        act_started = False
        detection_of_end = False
        print("gesture: " + current_gesture)
        current_gesture = ""

def detect_act():
    global current_gesture
    global act_started
    global act_stop_time
    act_stop_time = time.time()

    if act_stop_time - act_start_time > short_act_duration:
        count_l = acts.count('l')
        count_r = acts.count('r')
        count_b = acts.count('b')
        count_n = acts.count('_')
        max_act = max(count_l, count_r, count_b, count_n)
            
        if act_stop_time - act_start_time > long_act_duration:
            if max_act == count_l:
                 max_act = 'L'
            elif max_act == count_r:
                max_act = 'R'
            elif max_act == count_b:
                max_act = 'B'
            elif max_act == count_n:
                max_act = '_'
            current_gesture += max_act
        else:
            if max_act == count_l:
                max_act = 'l'
            elif max_act == count_r:
                max_act = 'r'
            elif max_act == count_b:
                max_act = 'b'
            elif max_act == count_n:
                max_act = '_'
            current_gesture += max_act
        print("act: " + max_act)
    
        


while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()

    rightClosed = gaze.is_closeRight()
    leftClosed = gaze.is_closeLeft()

    nothing = True
    
    if rightClosed:
        #text = "Closed left"
        listBlop["Closed left"]+=1
        nothing = False
    if leftClosed:
        listBlop["Closed right"]+=1
        nothing = False
    if nothing:
        listBlop["Nothing"]+=1
        
        #text = "Closed right"  
    #if rightClosed and leftClosed:   
        #text = "Closed both"


    #listBlop.append(text)

    counter += 1 

    if(counter==3):
        #print(listBlop)
        
        if listBlop["Closed left"] > listBlop["Closed right"]:
            text = "Closed left"
            detection_of_end = False
            start_act()
            if act_started == True:
                acts.append('l')
        elif listBlop["Closed right"] > listBlop["Closed left"]:
            text = "Closed right"
            detection_of_end = False
            start_act()
            if act_started == True:
                acts.append('r')
        elif listBlop["Nothing"] > listBlop["Closed right"] and listBlop["Nothing"] > listBlop["Closed left"]:
            text = ""
            if act_started == True:
                detect_act()
                acts = []
                act_started = False
                detection_of_end = True
                gestureEnd_start_time = time.time()
                gestureEnd_end_time = gestureEnd_start_time + gesture_end_duration
        elif listBlop["Closed right"] == listBlop["Closed left"]:
            text = "Closed both"
            detection_of_end = False
            start_act()
            if act_started == True:
                acts.append('b')

        if detection_of_end == True:
            detect_end()

        listBlop = {"Closed left":0,"Closed right":0,"Nothing":0}
        counter = 0



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
