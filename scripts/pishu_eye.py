#!/usr/bin/env python
import sys
import logging as log
import datetime as dt
from time import sleep, clock

import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera

import numpy
import math
import random

import rospy
from std_msgs.msg import String
from pishu_msgs.msg import MultiFaces, FacePosition


def main():
    rospy.init_node('eye', anonymous=False)

    talk_pub = rospy.Publisher("mouth/chatter", String, queue_size = 5)
    faces_pub = rospy.Publisher("eye/faces", MultiFaces, queue_size = 5)
    biggest_face_pub = rospy.Publisher("eye/biggest_face", FacePosition, queue_size = 5)

    print('sys.argv[0] =', sys.argv[0]) 

    faceCascade = cv2.CascadeClassifier('/home/pi/catkin_ws/src/pishu_eye/haarcascade_frontalface_default.xml')
    log.basicConfig(filename='webcam.log',level=log.INFO)

    camera = PiCamera()
    camera.resolution = (320, 240)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(320, 240))

    anterior = 0

    next_talk = clock() + random.uniform(2, 7)

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        
        image = frame.array


        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(24, 24)
        )

        biggest_face = 0
        face_pos = numpy.array([0.0, 0.0, 0.0])

        for (x, y, w, h) in faces:
            #cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            if w > biggest_face:
                face_pos = numpy.array([ x+w/2.0 - 160, -(y+h/2.0 - 120), w])
                biggest_face=w

#        if anterior != len(faces):
#           anterior = len(faces)
#            log.info("faces: "+str(len(faces))+" at "+str(dt.datetime.now()))

        if (cv2.waitKey(1) & 0xFF == ord('q')) | rospy.is_shutdown():
            break

        rawCapture.truncate(0)

        if biggest_face > 0:
            face_position = FacePosition(face_pos[0], face_pos[1], face_pos[2])
            biggest_face_pub.publish(face_position)

#            if next_talk < clock():
#                talk_pub.publish("I see you!")
#                next_talk = clock() + random.uniform(2, 7)



## Quitting



if __name__ == '__main__':
    main()  
