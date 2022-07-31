#!/usr/bin/env python
'''Animates distances and measurment quality'''
from rplidar import RPLidar
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import time
import utils

PORT_NAME = '/dev/ttyUSB0'
DMAX = 2000
IMIN = 0
IMAX = 50


class lidarModule():
    def update_line(num, iterator, line):
        scan = next(iterator)
        offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])
        line.set_offsets(offsets)
        intens = np.array([meas[0] for meas in scan])
        line.set_array(intens)
        return line,

    def getWallInFront(self):
        scan = next(self.iterator)
        totalChange = 0
        prevDist = scan[0][2]
        # print(i[0], i[1])
        distance = 0
        counter = 0
        rightMost = 0
        for i in scan:
            if(i[2] < 1000 and (i[1] > 315 or i[1] < 45)):
                currentDist = i[2]
                totalChange += currentDist - prevDist
                prevDist = currentDist
                counter += 1
                distance += currentDist
                if i[1] > rightMost:
                    rightMost = i[1]
        if counter != 0:
            return (distance/counter, totalChange)
        else:
            return (0, 0)

    def getWallInDirection(self, direction, range = 20):
        scan = next(self.iterator)
        distance = 0
        counter = 0
        directionLeft = direction - range
        directionRight = direction + range

        print(directionLeft)
        print(directionRight)
        for i in scan:
            print(i[1]-directionLeft)
            if(i[2] < 1000 and (i[1]-directionLeft > 0 and i[1]-directionLeft < directionRight)):
                counter += 1
                distance += i[2]
        if counter != 0:
            return distance/counter
        else:
            return 0

    def __init__(self):
        self.lidar = RPLidar(PORT_NAME)
        self.lidar.motor_speed = 0
        fig = plt.figure()
        ax = plt.subplot(111, projection='polar')
        # ax.set_theta_direction(-1)
        # ax.set_theta_offset(np.pi / 2.0)
        line = ax.scatter([0, 0], [0, 0], s=5, c=[IMIN, IMAX],
                          cmap=plt.cm.Greys_r, lw=0)
        ax.set_rmax(DMAX)
        ax.grid(True)
        self.iterator = self.lidar.iter_scans(max_buf_meas=2000)
        while True:
            before = time.time()
            self.getWallInFront(iterator=self.iterator)
            print(time.time() - before)
        ani = animation.FuncAnimation(fig, update_line,
                                      fargs=(iterator, line), interval=100)
        plt.show()

    def stop(self):
        self.lidar.stop()
        self.lidar.disconnect()

    # if __name__ == '__main__':
    #     run()
