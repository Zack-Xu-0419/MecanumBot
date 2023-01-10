from datetime import datetime
import math
from unittest import skip
import requests
import json
import time
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import pygame
import cv2 as cv
import threading
import sys

# constants
sleep = 0.01
autoDistanceMax = 400
robotAddress = "http://172.20.10.10:5000/"
imuIsOn = False
recordingData = False
print("imuStarted")
command_to_send = "imuStart"
auto = False
detectWalls = True

dataHistoryX = []
dataHistoryY = []
attitudeHistory = []
# Cartesian X
# Cartesian Y
cartX = []
cartY = []

dataRecorder = []  # Should be [    [[Angle, Distance], [Angle, DIstance]]    ]  Inner to outer = point -> set of points -> data across time

plt.ion()

ax = plt.subplot(projection='polar')
ax.grid(True)


plt.show()


pygame.init()
pygame.joystick.init()

print(pygame.joystick.get_count())


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
    for i in range(len(dataHistoryX)):
        cartX.append(
            dataHistoryY[i] * math.cos(dataHistoryX[i] + math.pi) + 3000)
        cartY.append(
            -dataHistoryY[i] * math.sin(dataHistoryX[i] + math.pi) + 3000)
    original = np.zeros((6000, 6000), dtype=np.uint8)
    original.fill(255)
    for x, y in zip(cartX, cartY):
        # print(x)
        original[int(x)-15:int(x)+15, int(y)-15:int(y)+15] = 0

    # original[3000:, :] = 255

    cv.imshow("img", original)

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

    cv.circle(original, (3000, 3000), 50, (0, 0, 255), 20)

    for i in final_keypoints:
        cv.circle(original, (int(i[0]), int(i[1])), 100, (0, 0, 255), 5)

    cv.imshow("A", original)

    # Go through the array and check for poles.
    return original


while True:
    print(dataHistoryX)
    print(dataHistoryY)
    r = requests.get(robotAddress)
    # print(r.text)

    data = json.loads(r.text.replace(
        '(', '[').replace(')', ']').replace("'", '"'))

    lidarData = data['lidar']
    imuData = data['imu']/17.288
    attitudeHistory.append(imuData)

    if len(attitudeHistory) > 100:
        attitudeHistory.pop(0)

    dataX = [theta / 180 * math.pi for [_, theta, _] in lidarData]
    dataY = [dist for [_, _, dist] in lidarData]
    dataHistoryX.extend(dataX)
    dataHistoryY.extend(dataY)

    while len(dataHistoryX) > 200:
        dataHistoryX.pop(0)

    while len(dataHistoryY) > 200:
        dataHistoryY.pop(0)

    # print(lidarData)
    ax.plot(dataHistoryX, dataHistoryY, "b.")
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2.0)
    if detectWalls:
        detectWallPlotting()

    ax.set_rmax(3000)
    plt.pause(0.01)
    for event in pygame.event.get():
        pass
    if(pygame.joystick.get_count() != 0):
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        x = 0
        y = 0
        turn = 0
        if not auto:
            x = joystick.get_axis(3) * 100
            y = joystick.get_axis(4) * -100
            turn = joystick.get_axis(0) * 50

        if joystick.get_button(3) == 1:
            detectWalls = not detectWalls

        if joystick.get_button(0) == 1:
            # "A"
            command_to_send = "stabilityControl"
        if joystick.get_button(10) == 1:
            auto = not auto
            if auto == True:
                print("auto on")
            else:
                print("auto off")
        # if joystick.get_button(9) == 1:
        #     rm = requests.post(robotAddress,
        #                        json={'angle': 0, 'power': 0, 'turn': 0})

        angle = math.atan2(x, y) * -1
        angle = math.degrees(angle)
        power = math.sqrt(x*x + y*y)

        rm = requests.post(robotAddress,
                           json={'cmd': command_to_send, 'angle': angle, 'power': power, 'turn': turn})

        command_to_send = ""

    ax.clear()
