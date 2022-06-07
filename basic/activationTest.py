import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(0, GPIO.OUT)
GPIO.output(0, True)
time.sleep(0.1)
GPIO.output(0, False)
GPIO.cleanup(0)