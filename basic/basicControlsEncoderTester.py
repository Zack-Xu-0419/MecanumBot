import basicControlsEncoder
import motorController
import time
import math
import pygame
import FaBo9Axis_MPU9250
import encoder
import threading


forward = [27, 6, 13, 16]
backward = [17, 5, 19, 26]
movement = basicControlsEncoder.robotMovement(forward, backward, False)

# movement.move(90, 100)
# time.sleep(0.2)
# movement.move(270, 100)
# time.sleep(0.2)
# movement.stop()

# Calibrate Heading
mpu9250 = FaBo9Axis_MPU9250.MPU9250()

result = 0

total = 0
for i in range(500):
    total += mpu9250.readGyro()['z']
offset = total/500

# BELOW IS JOYSTICK CONTROLLS

pygame.init()
pygame.joystick.init()


headingAssist = False
heading = 0


startTime = time.time()
prevError = 0

sleep = 0.001

pSet = 1.7 * sleep / 0.05
iSet = 0.6
dSet = 0.0008

I = 0

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
        exit()
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

        # for i in range(4):
            # position[i] = -1 * position[i]
        print(position)
        p = [-position[0], -position[1], -position[2], -position[3]]
        movement.setPower(p)
        # y = -position[0]
        y = 0
        x = 0

    if headingAssist:
        # Get current headingtimeDif = time.time() - startTime
        start = time.time()
        mag = mpu9250.readGyro()
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
