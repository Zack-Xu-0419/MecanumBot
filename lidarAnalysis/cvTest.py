import cv2 as cv
import math
import numpy as np
import matplotlib.pyplot as plt
dataHistoryX, dataHistoryY = zip(*eval(open("Run 2.txt").read())[0])
# print(dataHistoryY)
cartX = []
cartY = []
for i in range(len(dataHistoryX)):
    cartX.append(dataHistoryY[i] * math.cos(dataHistoryX[i]))
    cartY.append(dataHistoryY[i] * math.sin(dataHistoryX[i]))
abc = np.zeros((6000, 6000), dtype=np.uint8)
abc.fill(255)
for x, y in zip(cartX, cartY):
    # print(x)
    abc[int(x)-30:int(x)+30, int(y)-30:int(y)+30] = 0

plt.imshow(abc, cmap="gray")
a = cv.HoughLinesP(abc, 1, np.pi/180, 200)
