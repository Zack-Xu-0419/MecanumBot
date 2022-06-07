import motorController as controller
import time
import pygame
import math
import encoder

forward = [27, 6, 13, 16]
backward = [17, 5, 19, 26]


# power = controller.power()

# motorCtrl = controller.motorController(forward, backward)
# motorCtrl.runTest()
# time.sleep(2)
# motorCtrl.startPWM()
# time.sleep(2)


class robotMovement:
    def __init__(self, forward, backward, runTest):
        self.forward = forward
        self.backward = backward
        self.motor = controller.motorController(forward, backward)
        if runTest:
            self.motor.runTest()
        self.motor.startPWM()
        controller.power.activate(self)
        self.lastMoveTime = time.time()
        time.sleep(0.3)
        self.e = encoder.encoder([14, 18, 22, 15])
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
    
    def setPower(self, powers = []):
        if len(powers) != 0:
            print("NOTZERO")
            self.powers = powers
            # for i in range(4):
            #     self.powers[i] = -1 * self.powers[i]
            self.e.directionSet(2)
        counter = 0

        # Set Power
        print("PowerSet")
        print(self.powers)
        for i in self.powers:

            if(time.time() - self.lastMoveTime > 5):
                controller.power.activate(self)
            if(i > 100):
                i = 100
            if(i < -100):
                i = -100
            # print(i)
            if(i > 0):
                self.motor.pwmControl(self.forward[counter], i)
                self.motor.pwmControl(self.backward[counter], 0)
                self.e.directionSet(1)
            else:
                self.motor.pwmControl(self.backward[counter], -i)
                self.motor.pwmControl(self.forward[counter], 0)
                self.e.directionSet(-1)
            counter += 1
        self.lastMoveTime = time.time()

    def updateEncoder(self):
        self.e.record()
        # print(self.e.direction)

    def getPosition(self):
        return self.e.get()

    def stop(self):
        self.motor.stop()

    def on(self):
        controller.power.activate(self)
