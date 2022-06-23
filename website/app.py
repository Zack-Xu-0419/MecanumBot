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
import sys

sys.path.insert(0, "./basic")
import utils


forward = [27, 6, 13, 16]
backward = [17, 5, 19, 26]
movement = utils.robotMovement(forward, backward, False)


currentDirectory = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

app.secret_key = "Hspt"

color = datetime.now().hour


@app.route('/init', methods=["GET", "POST"])
def init():
    if request.method == "GET":
        return render_template("init.html")
    else:
        if request.form["password"] == "SHIELD":
            print("true")
            dbConnection = sqlite3.connect(currentDirectory + "/Home.db")
            initCursor = dbConnection.cursor()
            initCursor.execute(
                "CREATE TABLE IF NOT EXISTS bibleGuidelines(description TEXT, verse TEXT, category TEXT, toward TEXT, needWorkingOn BOOL, notes TEXT, provenUseful TEXT)")
            initCursor.execute(
                "CREATE TABLE IF NOT EXISTS countdown(description TEXT, initialDate DATE, targetDate DATE, person TEXT, priority INTEGER, displayUnit TEXT)")
            dbConnection.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route("/api/getRobotInfo", methods=["GET"])
def getRobotInfo():
    return {"odometryReading": movement.getPosition()}


@app.route("/run", methods=["GET"])
def run():
    global movement
    # Calibrate Heading
    mpu9250 = FaBo9Axis_MPU9250.MPU9250()

    result = 0

    total = 0
    for i in range(500):
        if mpu9250.readGyro()['z'] != "Offline":
            total += mpu9250.readGyro()['z']
    offset = total/500

    # BELOW IS JOYSTICK CONTROLLS

    pygame.init()
    pygame.joystick.init()


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

        # update encoder position and get encoder
        movement.updateEncoder()
        position = movement.getPosition()

        if encoderTest:
            print(position, end="")
            movement.setPower(
                [-position[0], -position[1], -position[2], -position[3]])

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
        elif(abs(heading - result) < 1 and not headingAssist and not encoderTest):
            movement.stop()
            # print("Stopped")

        time.sleep(sleep)

    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
