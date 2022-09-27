from datetime import datetime
import math
import requests
import json
import time
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import pygame

# constants
sleep = 0.01
robotAddress = "http://10.1.24.19:5000/"

plt.ion()

ax = plt.subplot(projection='polar')
ax.grid(True)

plt.show()


pygame.init()
pygame.joystick.init()

print(pygame.joystick.get_count())


while True:
    r = requests.get(robotAddress)

    data = json.loads(r.text.replace('(', '[').replace(')', ']'))

    dataX = [[theta / 180 * math.pi] for [_, theta, _] in data]
    dataY = [[dist] for [_, _, dist] in data]
    # print(data)
    ax.plot(dataX, dataY, "b.")
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2.0)

    # for i in tqdm(data):
    #     j += 1
    #     if j % 10 == 0:
    #         ax.plot(i[1]/180 * math.pi, i[2], "r.")

    ax.set_rmax(1000)
    plt.pause(0.01)
    for event in pygame.event.get():
        pass
    if(pygame.joystick.get_count() != 0):
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        x = joystick.get_axis(3) * 100
        y = joystick.get_axis(4) * -100
        turn = joystick.get_axis(0) * 50
        if joystick.get_button(7) == 1:
            headingAssist = True
        if joystick.get_button(6) == 1:
            headingAssist = False
        if joystick.get_button(3) == 1:
            pSet = float(input("P")) * sleep / 0.05
            iSet = float(input("I"))
            dSet = float(input("D"))
        if joystick.get_button(0) == 1:
            encoderTest = True
        if joystick.get_button(9) == 1:
            rm = requests.post(robotAddress,
                               json={'angle': 0, 'power': 0, 'turn': 0})

        angle = math.atan2(x, y) * -1
        angle = math.degrees(angle)
        power = math.sqrt(x*x + y*y)

        rm = requests.post(robotAddress,
                           json={'angle': angle, 'power': power, 'turn': turn})
    ax.clear()
