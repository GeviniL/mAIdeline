import numpy as np
import cv2
from mss.linux import MSS as mss 
import time


class GameCapture:
    def __init__(self, region = None, monitor_number = 1, downscale = 0.5):

        self.sct = mss()

        if region:
            self.monitor = region
        else:
            self.monitor = self.sct.monitors[monitor_number]

        self.downscale  = downscale
        self.last_frame_time = 0
        self.fps = 0

    def capture(self,grayscale = False):
        current_time = time.time()
        if self.last_frame_time > 0:
            self.fps = 1 / (current_time - self.last_frame_time)
        self.last_frame_time = current_time


        screenshot = np.array(self.sct.grab(self.monitor))

        if grayscale:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        else:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

        if self.downscale != 1.0:
            screenshot = cv2.resize(screenshot, (0,0), fx=self.downscale, fy=self.downscale)

    def detect_playe(self, frame):

        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        lower_pink = np.array([145, 100, 100])
        upper_pink = np.array([165, 255, 255])

        lower_red = np.array([170, 100, 100])
        upper_red = np.array([180, 255, 255])

        lower_blue = np.array([100, 100, 100])
        upper_blue = np.array([130, 255, 255])

        pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
        red_mask = cv2.inRange(hsv, lower_red, upper_red)
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

        pink_contours, _ = cv2.findContours(pink_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if pink_contours:
            largest = max(pink_contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 20:  # Minimum area threshold
                M = cv2.moments(largest)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return (cx, cy, 2)  # 2 dashes available

        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if red_contours:
            largest = max(red_contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 20:
                M = cv2.moments(largest)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return (cx, cy, 1)  # 1 dash available

        blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if blue_contours:
            largest = max(blue_contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 20:
                M = cv2.moments(largest)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return (cx, cy, 0)

        return None

    def get_game_state(self, frame):
        player_info = self.detect_player(frame)

        state = {
            'player_detected': player_info is not None,
        }






