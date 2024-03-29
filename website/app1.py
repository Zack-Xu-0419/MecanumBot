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
import pygame
import FaBo9Axis_MPU9250
from threading import Thread
import sys
import RPi.GPIO as GPIO

sys.path.insert(0, "../basic")


forward = [27, 6, 13, 16]
backward = [17, 5, 19, 26]
movement = utils.robotMovement(forward, backward, False)


# Calibrate Heading
mpu9250 = FaBo9Axis_MPU9250.MPU9250()


# BELOW IS JOYSTICK CONTROLLS

pygame.init()
pygame.joystick.init()


currentDirectory = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

app.secret_key = "Hspt"

color = datetime.now().hour

l = utils.lidarModule()

# Gyro variables
result = 0
total = 0
t = None  # gyro thread (we have to keep track of this to shut it off)

# Lidar Variables
scanResult = None
l = None  # lidar object (we have to keep track of this)
lt = None  # lidar Scanning thread


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route("/api/getRobotInfo", methods=["GET"])
def getRobotInfo():
    return {"odometryReading": movement.getPosition()}


scanResult = ""


@app.route("/api/getLidarScan", methods=["GET"])
def getLidarScan():
    return {"data": scanResult}


@app.route("/run", methods=["GET"])
def run():
    def run_robot():
        global scanResult
        result = 0

        total = 0
        for i in range(500):
            if mpu9250.readGyro()['z'] != "Offline":
                total += mpu9250.readGyro()['z']
        offset = total/500

        counter = 0

        headingAssist = False
        heading = 0

        startTime = time.time()
        prevError = 0

        sleep = 0.01

        pSet = 2 * sleep / 0.05
        iSet = 0.6
        dSet = 0.0008

        I = 0

        # robot position coordinate Tracker
        robotPosition = [0, 0]
        # Encoder - moved this to motorControllerEncoder
        # e = encoder.encoder(encoderPorts)
        encoderTest = False

        while True:
            scanResult = l.scan()
            for event in pygame.event.get():
                pass
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            x = joystick.get_axis(0) * 100
            y = joystick.get_axis(1) * -100
            if joystick.get_button(7) == 1:
                headingAssist = True
            if joystick.get_button(6) == 1:
                headingAssist = False
            if joystick.get_button(12) == 1:
                print("Breaking")
                break
            if joystick.get_button(3) == 1:
                pSet = float(input("P")) * sleep / 0.05
                iSet = float(input("I"))
                dSet = float(input("D"))
            if joystick.get_button(14) == 1:
                movement.on()
            if joystick.get_button(0) == 1:
                encoderTest = True
            if joystick.get_button(1) == 1:
                encoderTest = False
            if joystick.get_button(11) == 1:
                f = open(f"{counter}.txt", "a")
                for i in scanResult:
                    f.write(f"{i[1]}, {i[2]}\n")
                f.close()
                counter += 1

            if headingAssist:
                # Get current headingtimeDif = time.time() - startTime
                start = time.time()
                mag = mpu9250.readGyro()
                if str(mag['z']) != "Offline":
                    timeDif = time.time() - start
                    result += round((mag['z'] - offset) * (timeDif), 3) * 195
                    heading += joystick.get_axis(2) * -50

                    # PID
                    error = -(heading - result)

                    P = error * pSet
                    I += error * timeDif * iSet
                    I /= 2
                    D = ((prevError - error) / timeDif) * dSet
                    # print(f"P:{P}, I:{I}, D:{D}")
                    prevError = error
                    turn = (P+I-D)

                # movement.move(0, 0, (P+I-D))
                # print(f"MoveDirection: {(heading-result)}")
                # print(f"Target:{heading}")
                # print(f"Current: {result}")
            else:
                turn = joystick.get_axis(2) * 50

            # update encoder position and get encoder
            movement.updateEncoder(result/18.08)
            print(result/18.08)

            angle = math.atan2(x, y) * -1
            angle = math.degrees(angle)

            if angle < 0:
                angle += 180
                angle = 180 - angle * -1

            power = math.sqrt(x*x + y*y)

            if(power != 0 or abs(turn) > 0.5):
                # print("moving")
                if(power > 99):
                    power = 100
                if(turn != 0):
                    movement.move(angle, power, turn)
                else:
                    movement.move(angle, power)
            elif(abs(heading - result) < 1 or not headingAssist):
                movement.stop()
                # print("Stopped")

            time.sleep(sleep)
    runningRobot = Thread(target=run_robot)
    runningRobot.start()
    return render_template("index.html")


@app.route("/computerControl", methods=["GET", 'POST'])
def computerControl():
    global result
    global t
    global lt
    global l
    global scanResult
    input = request.json
    output = {}

    print(input)
    # No matter what, the RPi will always get a movement instruction from the computer (even if 0x, 0y, 0angle)
    if(input['command'] == "switch"):
        # Check for which to start
        values = input['values']
        if values[0] == 1:
            # Start Motor
            utils.power()
        if values[1] == 1:
            if t == None:
                # Start Thread to record gyro
                t = Thread(target=recordGyro)
                t.start()
        if values[2] == 1:
            # Start PWM for Lidar and read mode set to true.
            if l == None:
                print("Starting Lidar")
                l = utils.lidarModule()
                lt = Thread(target=idleScan)
                lt.start()

        # Record
        if l != None:
            print("Scanning")
            output["lidar"] = scanResult
    # It will change the movement direction of the robot until the computer send a newer information.
    if(input['command'] == "move"):
        values = input['values']
        movement.move(values[0], values[1], values[2])

    output['gyro'] = result
    # Then, it will return all the stats from the robot, both odometry and lidar.
    return output


def idleScan():
    global l
    global scanResult
    while True:
        scanResult = l.scan()
        print("F")


def recordGyro():
    global result
    global total

    # Calibrate Gyro

    for i in range(500):
        if mpu9250.readGyro()['z'] != "Offline":
            total += mpu9250.readGyro()['z']
    offset = total/500

    # Record Gyro
    while True:
        start = time.time()
        mag = mpu9250.readGyro()
        timeDif = time.time() - start
        result += round((mag['z'] - offset) * (timeDif), 3) * 195


if __name__ == '__main__':
    # start pwm for lidar

    app.run(debug=False, host='0.0.0.0')
