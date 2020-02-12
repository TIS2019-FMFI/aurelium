"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

from PIL import Image
from gaze_tracking import GazeTracking
import cv2
import time
import ctypes

user32 = ctypes.windll.user32
screeensize = user32.GetSystemMetrics(0),user32.GetSystemMetrics(1)
width = screeensize[0]
height = screeensize[1]

img_width = width//10 + 30
img_height = height//10
dim = (img_width,img_height)
alpha = 0.0 # priesvitnost obrazku

closedBothShort = cv2.imread("graphics/lcrc1.png") 
closedBothShort = cv2.resize(closedBothShort, dim, interpolation = cv2.INTER_AREA)
closedBothLong = cv2.imread("graphics/lcrc2.png") 
closedBothLong = cv2.resize(closedBothLong, dim, interpolation = cv2.INTER_AREA)

closedLeftShort = cv2.imread("graphics/lcro1.png") 
closedLeftShort = cv2.resize(closedLeftShort, dim, interpolation = cv2.INTER_AREA)
closedLeftLong = cv2.imread("graphics/lcro2.png") 
closedLeftLong = cv2.resize(closedLeftLong, dim, interpolation = cv2.INTER_AREA)

closedRightShort = cv2.imread("graphics/lorc1.png") 
closedRightShort = cv2.resize(closedRightShort, dim, interpolation = cv2.INTER_AREA)
closedRightLong = cv2.imread("graphics/lorc2.png") 
closedRightLong = cv2.resize(closedRightLong, dim, interpolation = cv2.INTER_AREA)

openBothShort = cv2.imread("graphics/loro1.png") 
openBothShort = cv2.resize(openBothShort, dim, interpolation = cv2.INTER_AREA)
openBothLong = cv2.imread("graphics/loro2.png") 
openBothLong = cv2.resize(openBothLong, dim, interpolation = cv2.INTER_AREA)



number_of_webcam = 0
gesture_end_duration = 0
short_act_duration = 0
long_act_duration = 0
result_display_duration = 0
current_gesture = ""

'''
gesta = {}           # Nacitaju sa so suboru
gesta['lrl']='Ahoj'  # gesta ako priklad po uspesnom vykonani sa vypise ahoj
gesta['l'] ='Ahoj'   # ked bude hotove nacitanie suboru tak toto zmazat
gesta['L']='Ahoj'
gesta['b'] ='Ahoj'
gesta['B']='Ahoj'
gesta['r'] ='Ahoj'
gesta['R']='Ahoj'
'''
textgesta =''
casVypisu = 0
koniecgesta= False

gests = {}

act_started = False
acts = []
act_start_time = time.time()
act_stop_time = time.time()
gesture_started = False
gestureEnd_start_time = time.time()
gestureEnd_stop_time = time.time()
detection_of_end = False

listValue = {"Closed left":0,"Closed right":0,"Nothing":0}
counter = 0
text = ""


maxim =0

def read_settings():
    global number_of_webcam
    global gesture_end_duration
    global short_act_duration
    global long_act_duration
    global result_display_duration
    with open('configuration.txt', 'r') as file:
        number_of_webcam = float(file.readline())
        gesture_end_duration = float(file.readline())/1000
        short_act_duration = float(file.readline())/1000
        long_act_duration = float(file.readline())/1000
        result_display_duration = float(file.readline())/1000
        for row in file:
            row = row.split('"')
            clear = []
            for i in row:
                if i != '':
                    clear.append(i)
            gesture = clear[2].strip("\n")
            gests[gesture] = clear[1]
        
        print('cislo kamery: ' , int(number_of_webcam))
        print('koniec gesta cas: ' , gesture_end_duration,"s")
        print('dlzka kratkeho: ' , short_act_duration,"s")
        print('dlzka dlheho: ' , long_act_duration,"s")
        print('dlzka zobrazenia: ' , result_display_duration,"s")
        print(gests)
        

def start_act():
    global act_started
    global act_start_time
    if act_started == False:
        act_started = True
        print('act started')
        act_start_time = time.time()

def detect_end():
    
    global koniecgesta
    global casVypisu
    global textgesta
    
    
    global gesture_started
    global current_gesture
    global detection_of_end
    if time.time() > gestureEnd_end_time:
        gesture_started = False
        act_started = False
        detection_of_end = False
        print("gesture: " + current_gesture) # Vypisovanie gest
        
        for i in gests:
            if(i == current_gesture):
                textgesta=gests[i]
                koniecgesta= True
                print(textgesta)

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
    
read_settings()

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
window_name = "Aurelium"

#cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()
    frame = cv2.flip(frame,1)

    # We send this frame to GazeTracking to analyze it
    try:
     gaze.refresh(frame)
    except:
        pass
    frame = gaze.annotated_frame()
    maxim = gaze.vratVelkostTvare()
    
    #if (maxim > 0):
    rightClosed,rightValue = gaze.is_closeRight()
    leftClosed,leftValue = gaze.is_closeLeft()

    nothing = True
    
    if rightClosed:
        listValue["Closed right"]+=1 
        if rightValue is not None and rightValue >= (gaze.eye_right_threshold - gaze.shift) and rightValue <= (gaze.eye_right_threshold + gaze.shift):
            gaze.addToThreshold("R",rightValue)
        nothing = False
    if leftClosed:
        listValue["Closed left"]+=1
        if leftValue is not None and leftValue >= (gaze.eye_left_threshold - gaze.shift) and leftValue <= (gaze.eye_left_threshold + gaze.shift):
            gaze.addToThreshold("L",leftValue)
        nothing = False
    if nothing:
        listValue["Nothing"]+=1
        
    counter += 1 

    if(counter==3):

        if(listValue["Closed right"]<listValue["Nothing"] and listValue["Closed left"]<listValue["Nothing"]):
            text = ""
            if act_started == True:
                detect_act()
                acts = []
                act_started = False
                detection_of_end = True
                gestureEnd_start_time = time.time()
                gestureEnd_end_time = gestureEnd_start_time + gesture_end_duration
                
        elif listValue["Closed right"] == listValue["Closed left"]:
            text = "Closed both"
            detection_of_end = False
            start_act()
            if act_started == True:
                acts.append('b')
        
        elif listValue["Closed left"] > listValue["Closed right"]:
            text = "Closed left"
            detection_of_end = False
            start_act()
            if act_started == True:
                acts.append('l')
                
        elif listValue["Closed right"] > listValue["Closed left"]:
            text = "Closed right"
            detection_of_end = False
            start_act()
            if act_started == True:
                acts.append('r')

        if detection_of_end == True:
            detect_end()

            if koniecgesta:
             koniecgesta = False   
             casVypisu = time.time()

        listValue = {"Closed left":0,"Closed right":0,"Nothing":0}
        counter = 0
            
     # Vypis po uspesnom vykonani gesta bude viditelny 5 sekund


    if((time.time() - casVypisu )< 5):
        cv2.putText(frame, textgesta, (90, 260), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
    else:
        textgesta=""

    if text== "Closed left":
        added_image = cv2.addWeighted(frame[0:img_height,0:img_width,:],alpha,closedLeftShort[0:img_height,0:img_width,:],1-alpha,0)
        frame[20:20+img_height,420:420+img_width] = added_image 
    elif text =="Closed right":
        added_image = cv2.addWeighted(frame[0:img_height,0:img_width,:],alpha,closedRightShort[0:img_height,0:img_width,:],1-alpha,0)
        frame[20:20+img_height,420:420+img_width] = added_image
    elif text =="Closed both":
        added_image = cv2.addWeighted(frame[0:img_height,0:img_width,:],alpha,closedBothShort[0:img_height,0:img_width,:],1-alpha,0)
        frame[20:20+img_height,420:420+img_width] = added_image
    else:
        added_image = None

    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    #cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    #cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    cv2.imshow("Aurelium", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cv2.destroyAllWindows()
