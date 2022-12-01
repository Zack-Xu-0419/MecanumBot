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

# constants
sleep = 0.01
autoDistanceMax = 400
robotAddress = "http://10.1.23.21:5000/"
imuIsOn = False
recordingData = False
command_to_send = " "
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


def detectWallPlotting():
    print(attitudeHistory)
    cartX = []
    cartY = []
    for i in range(len(dataHistoryX)):
        cartX.append(
            dataHistoryY[i] * math.cos(dataHistoryX[i] + math.pi - (attitudeHistory[-1]/180*math.pi)) + 3000)
        cartY.append(
            -dataHistoryY[i] * math.sin(dataHistoryX[i] + math.pi - (attitudeHistory[-1]/180*math.pi)) + 3000)
    original = np.zeros((6000, 6000), dtype=np.uint8)
    original.fill(255)
    for x, y in zip(cartX, cartY):
        # print(x)
        original[int(x)-30:int(x)+30, int(y)-30:int(y)+30] = 0

    cv.imshow("img", original)

    # annotatedColor = cv.cvtColor(original, cv.COLOR_GRAY2RGB)

    # blurred = cv.blur(original, ksize=(17, 17))
    # edges = cv.Canny(blurred, 80, 120, apertureSize=3)
    # lines = cv.HoughLinesP(edges, rho=2, theta=math.pi/360,
    #                        threshold=80, minLineLength=200, maxLineGap=200)
    # c = (255, 0, 0)
    # if lines is not None:
    #     for i in lines:
    #         line = i[0]
    #         cv.line(annotatedColor, (line[0], line[1]),
    #                 (line[2], line[3]), color=c, thickness=20)
    #     print(len(lines))
    #     cv.imshow("det", mat=cv.cvtColor(annotatedColor, cv.COLOR_RGB2BGR))


while True:
    r = requests.get(robotAddress)
    # print(r.text)

    data = json.loads(r.text.replace(
        '(', '[').replace(')', ']').replace("'", '"'))

    lidarData = data['lidar']
    imuData = data['imu']/17.288
    attitudeHistory.append(imuData)

    if len(attitudeHistory) > 50:
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

        if joystick.get_button(6) == 1:
            # Left thumb stick
            if imuIsOn:
                print("imuStopped")
                command_to_send = "imuStop"
            else:
                print("imuStarted")
                command_to_send = "imuStart"

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
