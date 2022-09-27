import utils
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

app = Flask(__name__)

# No matter what, when app start, start power, lidar, and init movement module

lidarValues = []

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
lidar = utils.lidarModule(80)


def lidarScanning():
    global lidarValues
    while True:
        try:
            lidarValues = lidar.scan()
        except KeyboardInterrupt:
            # lidar.kill()
            print('Safely exited lidar')


lidarThread = Thread(target=lidarScanning)
lidarThread.start()


@app.route("/", methods=["GET", "POST"])
def index():
    global lidarValues
    global movement
    if request.method == "GET":
        return str(lidarValues)
    if request.method == "POST":
        cmd = request.json
        if cmd['cmd'] == "imuStart":
            imu.track()
        if cmd['cmd'] == "imuStop":
            imu.stopTrack()
        else:
            movement.move(cmd['angle'], cmd['power'], cmd['turn'])
            return "200"


if __name__ == '__main__':
    # start pwm for lidar

    app.run(debug=False, host='0.0.0.0')
