import ast
import requests
import json
import time
import pygame

# constants
sleep = 0.01


input = {
    "command": "switch",
    "values": [0, 1, 1]
}


r = requests.post(
    'http://raspberrypi.local:5000/computerControl', json={
        "command": "switch",
        "values": [0, 0, 1]
    })


time.sleep(5)

requests.post(
    'http://raspberrypi.local:5000/computerControl', json={
        "command": "switch",
        "values": [0, 1, 0]
    })

while True:
    for event in pygame.event.get():
        pass
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    x = joystick.get_axis(0) * 100
    y = joystick.get_axis(1) * -100
    turn = joystick.get_axis(2) * 50
    if joystick.get_button(7) == 1:
        headingAssist = True
    if joystick.get_button(6) == 1:
        headingAssist = False
    if joystick.get_button(12) == 1:
        print("Breaking")
        break
    if joystick.get_button(3) == 1:
        pSet = float(input("P")) * sleep / 0.05
        iSet = float(input("I"))
        dSet = float(input("D"))
    if joystick.get_button(0) == 1:
        encoderTest = True
    if joystick.get_button(1) == 1:
        encoderTest = False

    m = requests.post(
        'http://raspberrypi.local:5000/computerControl', json={
            "command": "move",
            "values": [x, y, turn]
        })

    r = requests.post(
        'http://raspberrypi.local:5000/computerControl', json={
            "command": "switch",
            "values": [0, 0, 0]
        })
    print(r.text)
    time.sleep(0.3)
