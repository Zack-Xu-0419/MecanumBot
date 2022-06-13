import RPi.GPIO as GPIO
import time


class encoder:
    def __init__(self, ports):
        # RF, LB, LF, RB

        self.ports = ports
        self.directions = [1, 1, 1, 1]
        # 1 for positive, -1 for negative

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ports, GPIO.IN)

        self.previousStatusTracker = []
        self.totalTurns = []
        self.correctionMode = False

        for port, i in zip(ports, range(4)):
            self.previousStatusTracker.append(GPIO.input(port))
            self.totalTurns.append(0)
        print(self.previousStatusTracker)

    def directionSet(self, direction, item):
        self.directions[item] = direction

    def record(self):
        for port, i in zip(self.ports, range(4)):
            currentStatus = GPIO.input(port)
            if currentStatus != self.previousStatusTracker[i]:
                self.totalTurns[i] += 1 * self.directions[i]
                self.previousStatusTracker[i] = currentStatus

    def get(self):
        return self.totalTurns
