import basicControls
import time
import math
import pygame


forward = [27, 6, 13, 16]
backward = [17, 5, 19, 26]
movement = basicControls.robotMovement(forward, backward, False)

movement.move(90, 100)
time.sleep(1)
movement.move(270, 100)
time.sleep(1)
movement.stop()

# BELOW IS JOYSTICK CONTROLLS

pygame.init()
pygame.joystick.init()

lastMoveTime = time.time()

while True:
    for event in pygame.event.get():
        pass
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    x = joystick.get_axis(0) * 100
    y = joystick.get_axis(1) * -100
    turn = joystick.get_axis(2) * 50

    angle = math.atan2(x, y) * -1
    angle = math.degrees(angle)

    if angle < 0:
        angle += 180
        angle = 180 - angle * -1
    
    power = math.sqrt(x*x + y*y)

    print(angle, power)

    if(power != 0 or turn != 0):
        if(power > 99):
            power = 100
        if(turn != 0):
            movement.move(angle, power, turn)
        else:
            movement.move(angle, power)
    else:
        movement.stop()

    time.sleep(0.1)
