from __future__ import division
import os
import cv2
import dlib
from .eye import Eye
from .calibration import Calibration
import numpy


class GazeTracking(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.eye_left_threshold = 5
        self.eye_right_threshold = 5
        self.eyes_both_threshold = 10
        self.calibration = Calibration()
        self.previousStateLeft = None
        self.previousStateRight = None
        self.calibrationInProgress = False
        self.numberOfTimes = 30
        self.currentTimes = 0
        self.thresholds = {"right":self.eye_right_threshold,"left":self.eye_left_threshold,"both":0}
        self.thresholdsRight= []
        self.thresholdsLeft= []
        self.shift = 1
        self.facex1=0
        self.facey1 =0
        self.facex2 =0
        self.facey2 =0
        self.maxim =0
        self.facerecognization = False
        self.darkImageThreshold = 72
        
        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()

        # _predictor is used to get facial landmarks of a given face
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)

    @property
    def pupils_located(self):
        """Check that the pupils have been located"""
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            return False

    def calibrationThreshold(self):
        if self.eye_right.blinking >= (self.eye_right_threshold - self.shift) and self.eye_right.blinking <= (self.eye_right_threshold + self.shift) and len(self.thresholdsRight)<self.numberOfTimes:
            self.thresholdsRight.append(self.eye_right.blinking)

        if self.eye_left.blinking >= (self.eye_left_threshold - self.shift) and self.eye_left.blinking <= (self.eye_left_threshold + self.shift) and len(self.thresholdsLeft)<self.numberOfTimes:
            self.thresholdsLeft.append(self.eye_left.blinking)


    def changeThreshold(self):
        rightEye = sum(self.thresholdsRight)/len(self.thresholdsRight)
        leftEye = sum(self.thresholdsLeft)/len(self.thresholdsLeft)
            
        self.eye_right_threshold = rightEye + rightEye
        self.eye_left_threshold = leftEye + leftEye

        self.resetCalibration()
        

    def resetCalibration(self):
            self.calibrationInProgress = False
            self.currentTimes = 0
            self.thresholdsRight= []
            self.thresholdsLeft= []
        

    def _analyze(self):
        tvar = 0
        counter =0
        zoz = []
        pom = []
        self.facerecognization = False
        """Detects the face and initialize Eye objects"""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)
        for f in faces:
         self.facerecognization = True
         counter +=1
         pom.append(f.left())
         pom.append(f.top())
         pom.append(f.right())
         pom.append(f.bottom())
         zoz.append((f.bottom()-f.top())*(f.right()-f.left()))
         #print(f)
         #print(zoz)
        if(counter >0):
         self.maxim = max(zoz)  
         tvar = zoz.index(self.maxim)
         self.facex1= pom[tvar*4]
         self.facey1=pom[tvar*4+1]
         self.facex2=pom[tvar*4+2]
         self.facey2=pom[tvar*4+3]
    
        try:                    
            landmarks = self._predictor(frame, faces[tvar])            
            self.eye_left = Eye(frame, landmarks, 0, self.calibration)
            self.eye_right = Eye(frame, landmarks, 1, self.calibration)


            self.calibrationThreshold()

            if(len(self.thresholdsRight)==self.numberOfTimes and len(self.thresholdsLeft)==self.numberOfTimes):
                self.changeThreshold()


            if (self.previousStateLeft is None and self.previousStateRight is None):
                self.eye_left_threshold = 5
                self.eye_right_threshold = 5
                
 
        except IndexError:
            self.eye_left = None
            self.eye_right = None
            self.previousStateLeft = None
            self.previousStateRight = None
            self.resetCalibration()
          
    def refresh(self, frame):
        """Refreshes the frame and analyzes it.

        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        self._analyze()

    def pupil_left_coords(self):
        """Returns the coordinates of the left pupil"""
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def pupil_right_coords(self):
        """Returns the coordinates of the right pupil"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)

    def horizontal_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        horizontal direction of the gaze. The extreme right is 0.0,
        the center is 0.5 and the extreme left is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.x / (self.eye_left.center[0] * 2 - 10)
            pupil_right = self.eye_right.pupil.x / (self.eye_right.center[0] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def vertical_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        vertical direction of the gaze. The extreme top is 0.0,
        the center is 0.5 and the extreme bottom is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.y / (self.eye_left.center[1] * 2 - 10)
            pupil_right = self.eye_right.pupil.y / (self.eye_right.center[1] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def is_right(self):
        """Returns true if the user is looking to the right"""
        if self.pupils_located:
            return self.horizontal_ratio() <= 0.35

    def is_left(self):
        """Returns true if the user is looking to the left"""
        if self.pupils_located:
            return self.horizontal_ratio() >= 0.65

    def is_center(self):
        """Returns true if the user is looking to the center"""
        if self.pupils_located:
            return self.is_right() is not True and self.is_left() is not True

    def is_blinking(self):
        """Returns true if the user closes his eyes"""
        if self.pupils_located:
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking) / 2
            return blinking_ratio > self.eyes_both_threshold
    def is_closeRight(self):
        """Returns true if the user close right eye"""
        if self.pupils_located:
            blinking_ratio = (self.eye_right.blinking)
            return blinking_ratio > self.eye_right_threshold
    def is_closeLeft(self):
        """Returns true if the user close left eye"""
        if self.pupils_located:
            blinking_ratio = (self.eye_left.blinking)
            return blinking_ratio > self.eye_left_threshold

    def annotated_frame(self):
        """Returns the main frame with pupils highlighted"""
        frame = self.frame.copy()
        if self.imageTooDark():
            cv2.putText(frame, "Obraz je moc tmavy", (90, 260), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
            return frame
        
        if self.facerecognization == False:
         cv2.putText(frame, "Tvar nie je", (90, 260), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)   

        elif self.pupils_located:
            
            color = (0, 255, 0)
            x_left, y_left = self.pupil_left_coords()
            x_right, y_right = self.pupil_right_coords()

            if(self.maxim < 23000):
                cv2.putText(frame, "Tvar nie je dostatocne velka", (90, 260), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
            else:
                cv2.rectangle(frame,(self.facex1,self.facey1),(self.facex2,self.facey2),(255,0,0),2)
                cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), color)
                cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), color)
                cv2.line(frame, (x_right - 5, y_right), (x_right + 5, y_right), color)
                cv2.line(frame, (x_right, y_right - 5), (x_right, y_right + 5), color)

        return frame
    def vratVelkostTvare(self):
        return self.maxim

    def imageTooDarkFace(self,frame):
        cropFaceFrame = frame[self.facex1:self.facex2,self.facey1:self.facey2].copy() #v pripade zamerania sa iba na tvar
        print(numpy.mean(frame))
        return self.darkImageThreshold > numpy.mean(frame)

    def imageTooDark(self):
        #print(numpy.mean(self.frame))
        return self.darkImageThreshold > numpy.mean(self.frame,dtype=numpy.float64)

