import ctypes
import cv2
import time
from gaze_tracking import GazeTracking


class Program:
    def __init__(self):
        user32 = ctypes.windll.user32

        self.img_width = user32.GetSystemMetrics(0) // 5
        self.img_height = self.img_width // 2

        self.act = ""
        self.acts = []
        self.act_time = 0
        self.act_started = False
        self.act_ended = True
        self.act_start_time = time.time()
        self.act_stop_time = time.time()
        self.current_gesture = ""
        self.gesture_text = ""
        self.end_of_gesture = False
        self.gesture_end_start_time = time.time()
        self.gesture_end_stop_time = time.time()
        self.gests = dict()
        self.detection_of_end = False
        self.list_of_acts = {"Closed left": 0, "Closed right": 0, "Neither": 0}
        self.counter = 0
        self.time_of_output = 0
        self.end_of_display_image = True
        self.current_act = ""

        self.read_settings()

        self.gaze = GazeTracking()

        self.webcam = cv2.VideoCapture(self.webcam_number)
        self.webcam.set(3, self.webcam_width)
        self.webcam.set(4, self.webcam_height)

        self.screen_width = int(self.webcam.get(3))
        self.screen_height = int(self.webcam.get(4))

        window_name = "Aurelium"
        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        self.dim = (self.img_width, self.img_height)

        self.load_graphics()

        self.run()

        cv2.destroyAllWindows()

    def load_graphics(self):
        self.both_closed = cv2.imread("graphics/both_closed.png", -1)
        self.both_closed = cv2.resize(self.both_closed, self.dim)
        self.both_closed_long = cv2.imread("graphics/both_closed_long.png", -1)
        self.both_closed_long = cv2.resize(self.both_closed_long, self.dim)

        self.left_closed = cv2.imread("graphics/left_closed.png", -1)
        self.left_closed = cv2.resize(self.left_closed, self.dim)
        self.left_closed_long = cv2.imread("graphics/left_closed_long.png", -1)
        self.left_closed_long = cv2.resize(self.left_closed_long, self.dim)

        self.right_closed = cv2.imread("graphics/right_closed.png", -1)
        self.right_closed = cv2.resize(self.right_closed, self.dim)
        self.right_closed_long = cv2.imread("graphics/right_closed_long.png", -1)
        self.right_closed_long = cv2.resize(self.right_closed_long, self.dim)

        self.both_open = cv2.imread("graphics/both_open.png", -1)
        self.both_open = cv2.resize(self.both_open, self.dim)
        self.both_open_long = cv2.imread("graphics/both_open_long.png", -1)
        self.both_open_long = cv2.resize(self.both_open_long, self.dim)

    def read_settings(self):
        with open('configuration.txt', 'r') as file:
            self.webcam_number = int(file.readline())
            self.webcam_width = int(file.readline())
            self.webcam_height = int(file.readline())
            self.gesture_end_duration = float(file.readline()) / 1000
            self.short_act_duration = float(file.readline()) / 1000
            self.long_act_duration = float(file.readline()) / 1000
            self.result_display_duration = float(file.readline()) / 1000
            for row in file:
                row = row.split('"')
                clear = []
                for i in row:
                    if i != '':
                        clear.append(i)
                gesture = clear[2].strip("\n")
                self.gests[gesture] = clear[1]
        print(self.gests)

    def start_act(self):
        if self.act_started is False:
            self.act_started = True
            print('act started')
            self.act_start_time = time.time()

    def detect_act(self):
        self.act_stop_time = time.time()

        if self.act_stop_time - self.act_start_time > self.short_act_duration:
            count_l = self.acts.count('l')
            count_r = self.acts.count('r')
            count_b = self.acts.count('b')
            count_n = self.acts.count('_')
            max_act = max(count_l, count_r, count_b, count_n)

            if self.act_stop_time - self.act_start_time > self.long_act_duration:
                if max_act == count_l:
                    max_act = 'L'
                elif max_act == count_r:
                    max_act = 'R'
                elif max_act == count_b:
                    max_act = 'B'
                elif max_act == count_n:
                    max_act = '_'
                self.current_gesture += max_act
            else:
                if max_act == count_l:
                    max_act = 'l'
                elif max_act == count_r:
                    max_act = 'r'
                elif max_act == count_b:
                    max_act = 'b'
                elif max_act == count_n:
                    max_act = '_'
                self.current_gesture += max_act
            print("act: " + max_act)
            self.act = max_act
            self.act_ended = True

    def detect_end(self):
        if time.time() > self.gesture_end_stop_time:
            self.detection_of_end = False
            print("gesture: " + self.current_gesture)

            for i in self.gests:
                if i == self.current_gesture:
                    self.gesture_text = self.gests[i]
                    self.end_of_gesture = True
                    print(self.gesture_text)

            self.current_gesture = ""

    def run(self):
        while True:
            '''get a new frame from webcam'''
            _, self.frame = self.webcam.read()
            self.frame = cv2.flip(self.frame, 1)
            '''GazeTracking analyzes the frame'''
            try:
                self.gaze.refresh(self.frame)
            except Exception:
                pass
            self.frame = self.gaze.annotated_frame()

            if self.gaze.image_too_dark():
                cv2.putText(self.frame, "Nedostatok svetla", (10, self.screen_height - 10), cv2.FONT_HERSHEY_DUPLEX,
                            1.6, (50, 50, 200), 2)
            if self.gaze.face_recognition is False:
                cv2.putText(self.frame, "Neviem najst tvar", (10, self.screen_height - 70),
                            cv2.FONT_HERSHEY_DUPLEX, 1.6, (50, 50, 200), 2)
            if self.gaze.face_too_small is True:
                cv2.putText(self.frame, "Priblizte sa", (10, self.screen_height - 130),
                            cv2.FONT_HERSHEY_DUPLEX, 1.6, (50, 50, 200), 2)

            if self.current_gesture != "":
                cv2.putText(self.frame, self.current_gesture, (self.screen_width - self.img_width, self.img_height),
                            cv2.FONT_HERSHEY_DUPLEX, 1.6, (75, 75, 75), 2)

            self.which_eye_is_closed()

            self.which_act()

            if (time.time() - self.time_of_output) < 5:
                cv2.putText(self.frame, self.gesture_text, (10, 50), cv2.FONT_HERSHEY_DUPLEX, 1.6,
                            (75, 75, 75), 2)
            else:
                self.gesture_text = ""

            self.display_act()

            cv2.imshow("Aurelium", self.frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def which_eye_is_closed(self):
        right_is_closed, right_value = self.gaze.is_closed_right()
        left_is_closed, left_value = self.gaze.is_closed_left()

        neither = True

        if left_is_closed:
            self.list_of_acts["Closed left"] += 1
            if (right_value is not None and
                    (self.gaze.left_eye_threshold + self.gaze.shift) >= right_value >= (
                            self.gaze.left_eye_threshold - self.gaze.shift)):
                self.gaze.add_to_threshold("L", left_value)
            neither = False
        if right_is_closed:
            self.list_of_acts["Closed right"] += 1
            if (left_value is not None and
                    (self.gaze.right_eye_threshold + self.gaze.shift) >= left_value >= (
                            self.gaze.right_eye_threshold - self.gaze.shift)):
                self.gaze.add_to_threshold("R", right_value)
            neither = False
        if neither is True:
            self.list_of_acts["Neither"] += 1

    def which_act(self):
        self.counter += 1

        if self.counter == 3:
            if self.list_of_acts["Closed right"] < self.list_of_acts["Neither"] > self.list_of_acts["Closed left"]:
                self.current_act = ""
                if self.act_started is True:
                    self.detect_act()
                    if self.act_ended is True:
                        self.act_time = time.time()
                    self.acts = []
                    self.act_started = False
                    self.detection_of_end = True
                    self.gesture_end_start_time = time.time()
                    self.gesture_end_stop_time = self.gesture_end_start_time + self.gesture_end_duration
            elif self.list_of_acts["Closed right"] == self.list_of_acts["Closed left"]:
                self.current_act = "Closed both"
                self.detection_of_end = False
                self.start_act()
                self.acts.append("b")
            elif self.list_of_acts["Closed right"] < self.list_of_acts["Closed left"]:
                self.current_act = "Closed left"
                self.detection_of_end = False
                self.acts.append("l")
            elif self.list_of_acts["Closed right"] > self.list_of_acts["Closed left"]:
                self.current_act = "Closed right"
                self.detection_of_end = False
                self.acts.append("r")

            if self.detection_of_end is True:
                self.detect_end()
                if self.end_of_gesture is True:
                    self.end_of_gesture = False
                    self.time_of_output = time.time()

            self.list_of_acts = {"Closed left": 0, "Closed right": 0, "Neither": 0}
            self.counter = 0

    def display_act(self):
        no_image = True
        if self.end_of_display_image is True:
            no_image = False
            if self.current_act == "Closed left":
                self.act = ""
                self.act_ended = False
                added_image = self.display_image(self.left_closed)
            elif self.act_ended and self.act == "L":
                self.act = ""
                self.act_ended = False
                added_image = self.display_image(self.left_closed_long)
            elif self.current_act == "Closed right":
                self.act = ""
                self.act_ended = False
                added_image = self.display_image(self.right_closed)
            elif self.act_ended and self.act == "R":
                self.act = ""
                self.act_ended = False
                added_image = self.display_image(self.right_closed_long)
            elif self.current_act == "Closed both":
                self.act = ""
                self.act_ended = False
                added_image = self.display_image(self.both_closed)
            elif self.act_ended and self.act == "B":
                self.act = ""
                self.act_ended = False
                added_image = self.display_image(self.both_closed_long)
            elif self.gaze.pupils_located:
                added_image = self.display_image(self.both_open)
            else:
                no_image = True

        if (time.time() - self.act_time) < 1:
            self.end_of_display_image = False
        else:
            self.end_of_display_image = True

        if no_image is False:
            self.frame[0:self.img_height, self.screen_width - self.img_width:self.screen_width] = added_image

    def display_image(self, image):
        b, g, r, a = cv2.split(image)
        overlay_color = cv2.merge((b, g, r))
        mask = cv2.medianBlur(a, 5)
        h, w, _ = overlay_color.shape
        roi = self.frame[0:self.img_height, self.screen_width - self.img_width:self.screen_width]
        img1_bg = cv2.bitwise_and(roi.copy(), roi.copy(), mask=cv2.bitwise_not(mask))
        img2_fg = cv2.bitwise_and(overlay_color, overlay_color, mask=mask)
        added_image = cv2.add(img1_bg, img2_fg)
        return added_image


Program()
