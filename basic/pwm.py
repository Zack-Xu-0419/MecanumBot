import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


GPIO.setup(23, GPIO.OUT)

softpwm1 = GPIO.PWM(23, 50)

softpwm1.start(100)
softpwm1.ChangeDutyCycle(100)
time.sleep(5)
softpwm1.ChangeDutyCycle(40)
time.sleep(100)
#softpwm1.stop()
