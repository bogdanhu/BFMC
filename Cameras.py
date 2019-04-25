#! /usr/bin/python3
import cv2
import time
import threading
import numpy as np

#eg: https://github.com/task123/AutoTT/blob/master/Cameras.py

# sends messages stop_sign(),    to 'steering' set by set_steering(steering)
class Cameras:
    def __init__(self, motors, autoTTCommunication, streaming_port):
        # these values might change
        self.pin_battery_camera_1 = 13
        self.pin_battery_camera_2 = 8
        ##################################################
        # Values after this should not need to be changed.
        ##################################################



        self.image_1 = None
        self.image_2 = None
        self.blur_1 = None
        self.blur_2 = None

        self.frame_height = 300
        self.frame_width = 568
        self.jpeg_quality = 95
        self.stream_on = False
        self.reduse_stream_fps_by_a_factor = 1
        self.new_stream_image = False
        self.camera_1_on = False
        self.camera_2_on = False
        self.video_1 = None
        self.video_2 = None

        self.look_for_stop_sign = False
        self.look_for_speed_sign = False
        self.look_for_traffic_light = False

        self.draw_rectangles = False
        self.write_distances = False
        self.write_type_of_objects = False

        self.knn = cv2.ml.KNearest_create()
        self.knn_initialized = False

        self.ok_to_send_messages = True

        self.steering = None

        self.camera_thread = threading.Thread(target=self.camera_loop)
        self.camera_thread.setDaemon(True)
        self.camera_thread.start()

        #self.video_stream_thread = threading.Thread(target=self.video_stream_loop)
        #self.video_stream_thread.setDaemon(True)
        #self.video_stream_thread.start()

    def set_steering(self, steering):
        self.steering = steering

    def start_camera_1(self):
        self.arduino.digitalWrite(self.pin_battery_camera_1, 1)  # active high
        time.sleep(2)
        self.video_1 = cv2.VideoCapture(0)
        self.video_1.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.video_1.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.camera_1_on = True
        print("Accessing device's camera...")
        cap = cv2.VideoCapture(-1)  # seteaza camera implicita
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        ARIA_MAXIMA = width * height
        print("Aria maxima:\t" + str(ARIA_MAXIMA))
        print("\nFPS:\t" + str(fps))
        time.sleep(5)
        print("Camera ready")
