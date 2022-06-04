import motorController as controller
import time
import pygame

forward = [13, 27, 6, 16]
backward = [19, 17, 5, 26]


power = controller.power()

motorCtrl = controller.motorController(forward, backward)
motorCtrl.runTest()
time.sleep(2)
motorCtrl.startPWM()
time.sleep(2)



pygame.init()
pygame.joystick.init()

lastMoveTime = time.time()

while True:
    for event in pygame.event.get():
        pass
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    axis = joystick.get_axis(0)
    value = joystick.get_axis(1) * -100


    if value != 0:
        if time.time() - lastMoveTime > 5:
            print("Activated")
            power.activate()
        lastMoveTime = time.time()
    
    if value < 0:
        value *= -1
        motorCtrl.pwmControl(19, value)
        motorCtrl.pwmControl(17, value)
        motorCtrl.pwmControl(5, value)
        motorCtrl.pwmControl(26, value)

        motorCtrl.pwmControl(13, 0)
        motorCtrl.pwmControl(27, 0)
        motorCtrl.pwmControl(6, 0)
        motorCtrl.pwmControl(16, 0)
    else:
        
        motorCtrl.pwmControl(13, value)
        motorCtrl.pwmControl(27, value)
        motorCtrl.pwmControl(6, value)
        motorCtrl.pwmControl(16, value)

        motorCtrl.pwmControl(19, 0)
        motorCtrl.pwmControl(17, 0)
        motorCtrl.pwmControl(5, 0)
        motorCtrl.pwmControl(26, 0)
    

    time.sleep(0.1)