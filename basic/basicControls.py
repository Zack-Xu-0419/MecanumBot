import motorController as controller
import time

forward = [13, 27, 6, 16]
backward = [19, 17, 5, 26]

motorCtrl = controller.motorController(forward, backward)
motorCtrl.runTest()
time.sleep(2)
motorCtrl.startPWM()
motorCtrl.pwmControl(13, 50)
time.sleep(5)