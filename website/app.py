from concurrent.futures import thread
import sqlite3
import os
import datetime
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

sys.path.insert(0, "../basic")
import utils

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


@app.route("/", methods=["GET", "POST"])
def index():
    global lidarValues
    global movement
    global stability_control
    global scThread
    global currentMovement
    global offset
    if request.method == "GET":
        return str({"lidar":lidarValues, "imu": imu.getAngle()})
    if request.method == "POST":
        cmd = request.json
        print(cmd)
        if cmd['cmd'] == "imuStart":
            print("started tracking")
            imu.track()
        if cmd['cmd'] == "imuStop":
            print("stopped tracking")
            imu.stopTrack()
        if cmd['cmd'] == "stabilityControl":
            stability_control = not stability_control
            if stability_control:
                scThread = Thread(target=sc)
                scThread.start()
            else:
                scThread.join()
        else:
            if(stability_control):
                currentMovement = [cmd['angle'], cmd['power'], cmd['turn']]
                offset += cmd['turn']
                return "200"
            else:
                movement.move(cmd['angle'], cmd['power'], cmd['turn'])
                return "200"
                

def sc():
    global angle
    global currentMovement
    global offset
    while True:
        angle = imu.getAngle() + offset *10
        movement.move(currentMovement[0], currentMovement[1], angle/10)
        time.sleep(0.01)


if __name__ == '__main__':
    # start pwm for lidar

    app.run(debug=False, host='0.0.0.0')
