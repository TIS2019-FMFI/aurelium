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
        self.left_eye_threshold = 5
        self.right_eye_threshold = 5
        self.eyes_both_threshold = 10
        self.calibration = Calibration()
        self.face_x1 = 0
        self.face_y1 = 0
        self.face_x2 = 0
        self.face_y2 = 0
        self.maxim = 0
        self.face_recognition = False
        self.darkImageThreshold = 92
        self.thresholdsRight = []
        self.thresholdsLeft = []
        self.shift = 2
        self.numberOfTimes = 10
        self.calibrate = True
        self.currentNumberOfTimes = 0

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

    def calibration_threshold(self):
        if (self.right_eye_threshold - self.shift) <= self.eye_right.blinking <= (
                self.right_eye_threshold + self.shift) and len(self.thresholdsRight) < self.numberOfTimes:
            self.thresholdsRight.append(self.eye_right.blinking)

        if (self.left_eye_threshold - self.shift) <= self.eye_left.blinking <= (
                self.left_eye_threshold + self.shift) and len(self.thresholdsLeft) < self.numberOfTimes:
            self.thresholdsLeft.append(self.eye_left.blinking)

    def add_to_threshold(self, eye, value):
        if value is not None:
            if eye == "R":
                self.thresholdsRight.append(value)
            elif eye == "L":
                self.thresholdsLeft.append(value)

    def reset_calibration(self):
        self.thresholdsRight = []
        self.thresholdsLeft = []

    def change_threshold(self):
        if len(self.thresholdsRight) == self.numberOfTimes:
            right_eye = sum(self.thresholdsRight) / len(self.thresholdsRight) - (
                    sum(self.thresholdsRight) / len(self.thresholdsRight)) * 0.10
            self.right_eye_threshold = (self.right_eye_threshold + right_eye) / 2
            self.thresholdsRight = []
        else:
            left_eye = sum(self.thresholdsLeft) / len(self.thresholdsLeft) - (
                    sum(self.thresholdsLeft) / len(self.thresholdsLeft)) * 0.10
            self.left_eye_threshold = (self.left_eye_threshold + left_eye) / 2
            self.thresholdsLeft = []

        self.eyes_both_threshold = (self.right_eye_threshold + self.left_eye_threshold) + (
                self.right_eye_threshold + self.left_eye_threshold) * 0.22

        #print(str(self.right_eye_threshold) + " " + str(self.left_eye_threshold))

    def _analyze(self):
        face = 0
        counter = 0
        zoz = []
        pom = []
        self.face_recognition = False
        """Detects the face and initialize Eye objects"""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)
        for f in faces:
            self.face_recognition = True
            counter += 1
            pom.append(f.left())
            pom.append(f.top())
            pom.append(f.right())
            pom.append(f.bottom())
            zoz.append((f.bottom() - f.top()) * (f.right() - f.left()))
        if counter > 0:
            self.maxim = max(zoz)
            face = zoz.index(self.maxim)
            self.face_x1 = pom[face * 4]
            self.face_y1 = pom[face * 4 + 1]
            self.face_x2 = pom[face * 4 + 2]
            self.face_y2 = pom[face * 4 + 3]

        try:
            landmarks = self._predictor(frame, faces[face])
            self.eye_left = Eye(frame, landmarks, 0, self.calibration)
            self.eye_right = Eye(frame, landmarks, 1, self.calibration)

            if len(self.thresholdsRight) == self.numberOfTimes or len(self.thresholdsLeft) == self.numberOfTimes:
                self.change_threshold()

        except IndexError:
            self.left_eye_threshold = 5
            self.right_eye_threshold = 5
            self.eyes_both_threshold = 10
            self.reset_calibration()
            self.eye_left = None
            self.eye_right = None

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
            return x, y

    def pupil_right_coords(self):
        """Returns the coordinates of the right pupil"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return x, y

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

    def is_closed_right(self):
        """Returns true if the user closes right eye"""
        if self.pupils_located:
            blinking_ratio = self.eye_right.blinking
            return blinking_ratio > self.right_eye_threshold, blinking_ratio
        return False, None

    def is_closed_left(self):
        """Returns true if the user closes left eye"""
        if self.pupils_located:
            blinking_ratio = self.eye_left.blinking
            return blinking_ratio > self.left_eye_threshold, blinking_ratio
        return False, None

    def annotated_frame(self):
        """Returns the main frame with pupils highlighted"""
        frame = self.frame.copy()

        if self.pupils_located:
            if self.maxim < 23000:
                cv2.putText(frame, "Tvar nie je dostatocne velka", (90, 260), cv2.FONT_HERSHEY_DUPLEX, 1.6,
                            (255, 255, 255), 2)
            else:
                cv2.rectangle(frame, (self.face_x1, self.face_y1), (self.face_x2, self.face_y2), (255, 255, 255), 2)
                '''
                cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), color)
                cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), color)
                cv2.line(frame, (x_right - 5, y_right), (x_right + 5, y_right), color)
                cv2.line(frame, (x_right, y_right - 5), (x_right, y_right + 5), color)
                '''

        return frame

    def return_face_size(self):
        return self.maxim

    def image_too_dark(self):
        if self.face_x1 >= 0 and self.face_x2 >= 0 and self.face_y1 >= 0 and self.face_y2 >= 0:
            frame = self.frame[self.face_x1:self.face_x2, self.face_y1:self.face_y2].copy()
            # in case of focusing on the face only
        else:
            frame = self.frame.copy()
        return self.darkImageThreshold > numpy.mean(frame, dtype=numpy.float64)
