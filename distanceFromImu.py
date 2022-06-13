import time
import math
import pygame
import FaBo9Axis_MPU9250

# Doesn't seem like this is possible
# Calibrate Heading
mpu9250 = FaBo9Axis_MPU9250.MPU9250()
result = 0

total = 0
for i in range(500):
    total += mpu9250.readAccel()['y']
offset = total/500

startTime = time.time()

distance = 0

while True:
    # Speed
    r = mpu9250.readAccel()['y'] - offset
    dt = time.time() - startTime
    r = round(r, 3)
    result += r * dt

    # Distance
    distance += result * dt
    
    print(distance, result)

    startTime = time.time()

    time.sleep(0.05)
