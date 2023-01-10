import utils
import time
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, request, url_for, render_template, redirect, session
import time
import math
# import pygame
import FaBo9Axis_MPU9250
from threading import Thread
import sys
import RPi.GPIO as GPIO
import cv2 as cv
import numpy as np

sys.path.insert(0, "./basic")


app = Flask(__name__)

# Robot Modes
stability_control = False
currentMovement = [0, 0, 0]
angle = 0
offset = 0

# No matter what, when app start, start power, lidar, and init movement module

# Lidar global values and max range
lidarValues = []
maxRange = 1000

# Initiate Ports as out
forward = [27, 6, 13, 16]
backward = [17, 5, 19, 26]

# Start power
power = utils.power()
power.activate()
# TODO: start tracking

imu = utils.imu()

movement = utils.robotMovement(forward, backward, False)

# Start lidar
lidar = utils.lidarModule(40)


def lidarScanning():
    global lidarValues
    while True:
        try:
            lidarValues = lidar.scan()
            # i = 0
            # while i < len(lidarValues):
            #     # print(lidarValues[i][2])
            #     if lidarValues[i][2] > maxRange:
            #         lidarValues.pop(i)
            #     else:
            #         i+=1
        except KeyboardInterrupt:
            # lidar.kill()
            print('Safely exited lidar')


lidarThread = Thread(target=lidarScanning)
lidarThread.start()


def remove_close_points(points):
    # Create a new array to store the points that are not within 10 pixels of each other
    new_points = []

    # Iterate over the points in the input array
    for i in points:
        x = i[0]
        y = i[1]
        found = False
        for j in points:
            if(i == j).all():
                continue
            if(((x-j[0])**2 + (y-j[1])**2) < 100000):
                found = True
                break
        if not found:
            new_points.append(i)

    # Return the new array of points
    return np.array(new_points)


def detectWallPlotting():
    keypoints_coord = []
    cartX = []
    cartY = []
    for i in range(len(lidarValues)):
        cartX.append(
            lidarValues[i] * math.cos(lidarValues[i] + math.pi) + 3000)
        cartY.append(
            -lidarValues[i] * math.sin(lidarValues[i] + math.pi) + 3000)
    original = np.zeros((6000, 6000), dtype=np.uint8)
    original.fill(255)
    for x, y in zip(cartX, cartY):
        # print(x)
        original[int(x)-15:int(x)+15, int(y)-15:int(y)+15] = 0

    # original[3000:, :] = 255

    # cv.imshow("img", original)

    params = cv.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 5
    params.maxThreshold = 200

    # Filter by Area.
    params.filterByArea = True
    params.minArea = 2

    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.01

    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.05

    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01

    detector = cv.SimpleBlobDetector_create(params)

    # print(dir(detector))

    # Detect blobs.
    keypoints = detector.detect(original)

    print(keypoints)

    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob

    for point in keypoints:
        keypoints_coord.append([point.pt[0], point.pt[1]])

    keypoints_coord = np.array(keypoints_coord)
    print(keypoints_coord)
    final_keypoints = remove_close_points(keypoints_coord)

    # cv.circle(original, (3000, 3000), 50, (0, 0, 255), 20)

    for i in final_keypoints:
        # cv.circle(original, (int(i[0]), int(i[1])), 100, (0, 0, 255), 5)
        print(i[0])
        print(i[1])

    # Go through the array and check for poles.
    return keypoints


time.sleep(1)
for i in range(10):
    detectWallPlotting()
    time.sleep(1)

# Initialization


# while True:
#     # Robot Movements

#     # Localization
