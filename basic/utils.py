import time
import pygame
import math
import RPi.GPIO as GPIO
import rplidar as RPLidar

forward = [27, 6, 13, 16]
backward = [17, 5, 19, 26]

PORT_NAME = '/dev/ttyUSB0'
DMAX = 2000
IMIN = 0
IMAX = 50


class robotMovement:
    def __init__(self, forward, backward, runTest):
        self.forward = forward
        self.backward = backward
        self.motor = motorController(forward, backward)
        if runTest:
            self.motor.runTest()
        self.motor.startPWM()
        power.activate(self)
        self.lastMoveTime = time.time()
        time.sleep(0.3)
        self.o = encoder([14, 18, 22, 15])
        self.powers = [0, 0, 0, 0]

    def move(self, angle, power, turn=0):
        self.powers = []
        self.powers.append(
            power * math.sin(math.radians(angle + 45)) - turn)  # RightFront
        self.powers.append(self.powers[0] + 2 * turn)  # LeftBack
        self.powers.append(
            power * math.cos(math.radians(angle + 45)) + turn)  # LeftFront
        self.powers.append(self.powers[2] - 2 * turn)  # RightBack

        self.setPower()

    def setPower(self, powers=[]):
        if len(powers) != 0:
            # print("D Overide")
            self.powers = powers
        counter = 0

        # Set Power
        # print("PowerSet")
        for i in self.powers:
            # print(round(i, 2))
            # if(time.time() - self.lastMoveTime > 5):
            #     power.activate(self)
            if(i > 100):
                i = 100
            if(i < -100):
                i = -100
            # print(i)
            if(i > 0):
                self.motor.pwmControl(self.forward[counter], i)
                self.motor.pwmControl(self.backward[counter], 0)
                self.o.directionSet(1, counter)
            else:
                self.motor.pwmControl(self.backward[counter], -i)
                self.motor.pwmControl(self.forward[counter], 0)
                self.o.directionSet(-1, counter)
            counter += 1
        self.lastMoveTime = time.time()

    def updateEncoder(self):
        self.o.record()
        # print(self.o.direction)

    def getPosition(self):
        return self.o.get()

    def stop(self):
        self.motor.stop()

    def on(self):
        power.activate(self)


class motorController:
    def __init__(self, portsForward, portsBackward):
        GPIO.setmode(GPIO.BCM)
        self.portsForward = portsForward
        setup(self.portsForward)
        self.portsBackward = portsBackward
        setup(self.portsBackward)
        self.motors = []
        self.o = odometry([14, 18, 22, 15])

    def runTest(self):
        GPIO.output(13, GPIO.HIGH)
        for i in self.portsForward:
            print(i)
            GPIO.output(i, GPIO.HIGH)
        time.sleep(0.2)
        for i in self.portsForward:
            GPIO.output(i, GPIO.LOW)

        for i in self.portsBackward:
            print(i)
            GPIO.output(i, GPIO.HIGH)
        time.sleep(0.2)
        for i in self.portsBackward:
            GPIO.output(i, GPIO.LOW)

    def startPWM(self):
        for i in self.portsForward:
            # Create PWM instance and add to self.motors
            softPWM = GPIO.PWM(i, 30)
            softPWM.start(0)
            self.motors.append(softPWM)
        for i in self.portsBackward:
            # Create PWM instance and add to self.motors
            softPWM = GPIO.PWM(i, 30)
            softPWM.start(0)
            self.motors.append(softPWM)

    def pwmControl(self, portNumber, dutyCycle):
        ports = self.portsForward + self.portsBackward
        index = ports.index(portNumber)
        self.motors[index].ChangeDutyCycle(math.sqrt(dutyCycle/100) * 100)
        # if forward
        if index < 4:
            self.o.directionSet(1, index)
        else:
            self.o.directionSet(-1, index - 4)

    def getEncoderValue(self):
        return self.o.get()

    def updateEncoderValue(self):
        self.o.record()

    def stop(self):
        for i in self.portsForward + self.portsBackward:
            self.pwmControl(i, 0)


class setup():
    def __init__(self, ports):
        GPIO.setmode(GPIO.BCM)
        for i in ports:
            GPIO.setup(i, GPIO.OUT)


class power():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(0, GPIO.OUT)
        GPIO.output(0, True)
        time.sleep(0.1)
        GPIO.output(0, False)
        GPIO.cleanup(0)
        time.sleep(0.3)

    def activate(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(0, GPIO.OUT)
        GPIO.output(0, True)
        time.sleep(0.1)
        GPIO.output(0, False)
        GPIO.cleanup(0)
        time.sleep(0.3)


class lidarModule():
    def getWallInFront(self):
        scan = next(self.iterator)
        totalChange = 0
        prevDist = scan[0][2]
        # print(i[0], i[1])
        distance = 0
        counter = 0
        rightMost = 0
        for i in scan:
            if(i[2] < 1000 and (i[1] > 315 or i[1] < 45)):
                currentDist = i[2]
                totalChange += currentDist - prevDist
                prevDist = currentDist
                counter += 1
                distance += currentDist
                if i[1] > rightMost:
                    rightMost = i[1]
        if counter != 0:
            return distance/counter
        else:
            return 0

    def getWallInDirection(self, direction, range=20):

        if(direction - range < 0):
            self.directionLeft = direction
            self.directionRight = direction + 2 * range
        else:
            self.directionLeft = direction - range
            self.directionRight = direction + range

        scan = next(self.iterator)
        distance = 0
        counter = 0

        for i in scan:
            d = i[1]
            # if i[2] < 400:
            #     print(d)
            d += range
            if d > 360:
                d -= 360
            if((d-self.directionLeft > 0 and d-self.directionLeft < self.directionRight)):
                # print(i[1])
                counter += 1
                distance += i[2]
        if counter != 0:
            return distance/counter
        else:
            return 0

    def __init__(self):
        self.directionLeft = 0
        self.directionRight = 0
        self.lidar = RPLidar.RPLidar(PORT_NAME)
        self.lidar.motor_speed = 0
        self.iterator = self.lidar.iter_scans(max_buf_meas=2000)

    def stop(self):
        self.lidar.stop()
        self.lidar.disconnect()


class odometry:
    def __init__(self, ports):
        # Left front, Left

        self.ports = ports
        self.directions = [1, 1]
        # 1 for positive, -1 for negative

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ports, GPIO.IN)

        self.previousStatusTracker = []
        self.totalTurns = []
        self.correctionMode = False

        for port, i in zip(ports, range(2)):
            self.previousStatusTracker.append(GPIO.input(port))
            self.totalTurns.append(0)
        print(self.previousStatusTracker)

    def directionSet(self, direction, item):
        self.directions[item] = direction

    def record(self):
        for port, i in zip(self.ports, range(2)):
            currentStatus = GPIO.input(port)
            if currentStatus != self.previousStatusTracker[i]:
                self.totalTurns[i] += 1 * self.directions[i]
                self.previousStatusTracker[i] = currentStatus

    def get(self):
        return self.totalTurns
