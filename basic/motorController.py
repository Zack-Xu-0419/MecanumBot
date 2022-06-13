import RPi.GPIO as GPIO
import time
import math

class motorController:
    def __init__(self, portsForward, portsBackward):
        GPIO.setmode(GPIO.BCM)
        self.portsForward = portsForward
        setUp = setup(self.portsForward)
        self.portsBackward = portsBackward
        setUp = setup(self.portsBackward)
        self.motors = []
    
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