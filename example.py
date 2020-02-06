"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

from gaze_tracking import GazeTracking
import cv2
import time

simg = cv2.imread("both_closed.png") # Nacitany obrazok
alpha = 0.0 # priesvitnost obrazku

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
window_name = "Demo"
number_of_webcam = 0


#cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
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

listBlop = {"Closed left":0,"Closed right":0,"Nothing":0}
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
        number_of_webcam = float(file.readline())/1000
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
        
        print('cislo kamery: ' , number_of_webcam)
        print('koniec gesta cas: ' , gesture_end_duration)
        print('dlzka kratkeho: ' , short_act_duration)
        print('dlzka dlheho: ' , long_act_duration)
        print('dlzka zobrazenia: ' , result_display_duration)
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
while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()
    frame = cv2.flip(frame,1)

    
    added_image = cv2.addWeighted(frame[0:180,0:180,:],alpha,simg[0:180,0:180,:],1-alpha,0)
    # frame [0:180,0:180,:] netreba menit  
    # simg [0:180,0:180,:] urcuje vysku a sirku obrazka teraz je to 180 180 
    frame[20:200,420:600] = added_image # umiestnenie obrazka na obrazovke
    # Pri vsetkych 3 premennych musi byt rozdiel medzi druhym a prvym cislom rovnaky

    
    # We send this frame to GazeTracking to analyze it
    try:
     gaze.refresh(frame)
    except:
        pass
    frame = gaze.annotated_frame()
    maxim = gaze.vratVelkostTvare()
    
    #if (maxim > 23000):
    rightClosed,rightValue = gaze.is_closeRight()
    leftClosed,leftValue = gaze.is_closeLeft()

    nothing = True
    
    if rightClosed:
        listBlop["Closed left"]+=1
        if rightValue is not None and rightValue >= (gaze.eye_right_threshold - gaze.shift) and rightValue <= (gaze.eye_right_threshold + gaze.shift):
            #listValue["L"]+=rightValue
            gaze.addToThreshold("L",rightValue)
        nothing = False
    if leftClosed:
        listBlop["Closed right"]+=1       
        if leftValue is not None and leftValue >= (gaze.eye_left_threshold - gaze.shift) and leftValue <= (gaze.eye_left_threshold + gaze.shift):
            #listValue["R"]+=leftValue
            gaze.addToThreshold("R",leftValue)
        nothing = False
    if nothing:
        listBlop["Nothing"]+=1
        
    counter += 1 

    if(counter==3):

        if(listBlop["Closed right"]<listBlop["Nothing"] and listBlop["Closed left"]<listBlop["Nothing"]):
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
        
        elif listBlop["Closed left"] > listBlop["Closed right"]:
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

        if detection_of_end == True:
            detect_end()

            if koniecgesta:
             koniecgesta = False   
             casVypisu = time.time()

        listBlop = {"Closed left":0,"Closed right":0,"Nothing":0}
        listValue = {"L":0,"R":0}
        counter = 0
            
     # Vypis po uspesnom vykonani gesta bude viditelny 5 sekund


    if((time.time() - casVypisu )< 5):
        cv2.putText(frame, textgesta, (90, 260), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
    else:
        textgesta=""

    
    '''
    if text== "Closed left":
        added_image = cv2.addWeighted(frame[150:350,150:350,:],alpha,simg[0:200,0:200,:],1-alpha,0)
        frame[20:220,150:350] = added_image
    else:
        added_image = None
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
