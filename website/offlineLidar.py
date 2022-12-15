from datetime import datetime
import math
from unittest import skip
import requests
import json
import time
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import cv2 as cv
import numpy as np

coordinates = [0, 0]

dataHistoryX = [4.0431642953231135, 4.069071526407405, 4.079979834232369, 4.103432696056044, 4.180608973917668, 4.427409438457491, 4.463952269671122, 4.476224115974206, 4.488495962277292, 4.499404270102256, 4.511676116405342, 4.524766085795299, 4.53676522440276, 4.5484916553145975, 4.561854332400179, 4.574398886398888, 4.58448907113698, 4.5986698713094345, 4.646666425739278, 4.883922120932257, 4.887194613279747, 4.909011228929676, 4.919374121363393, 4.878740674715399, 4.890739813322861, 4.999004768485634, 5.011276614788718, 5.023275753396179, 5.035002184308016, 5.047274030611102, 5.49724172839089, 5.509786282389599, 5.521512713301436, 5.772131085579996, 5.930574256737606, 5.942573395345068, 5.9542998262569045, 5.967117087951238, 5.978843518863075, 6.003114503773621, 6.01565905777233, 6.047020442769103, 6.127196505282593, 6.139468351585678, 6.24364269131409, 6.2559145376171745, 6.2679136762246355, 6.280458230223345, 0.009272061651219875, 0.021543907954305004, 0.033270338866141905, 0.04581489286485115, 0.10635600129340445, 0.11862784759648957, 0.13062698620395058, 0.14317154020265985, 0.17998707911191522, 0.1911680946325039, 0.20316723323996494, 0.23698298749735505, 0.2645264647553906, 0.2765256033628516, 0.2882520342746885, 0.3002511728821495, 0.3127957268808587, 0.32506757318394386, 0.337339419487029, 0.3496112657901141, 0.40224385104556815, 0.41260674347928444, 0.4237877589998731, 0.4376958514767029, 0.44887686699729157, 0.4611487133003767, 0.4720570211253413, 0.4862378212977952, 0.518962744772689, 0.5312345910757741, 0.543233729683235, 0.5557782836819444, 0.5677774222894053, 0.5797765608968664, 0.5920484071999514, 0.6234097921967245, 0.6520441002372566, 0.6637705311490935, 0.6757696697565545, 0.6883142237552637, 0.7003133623627248, 0.7120397932745617, 0.7245843472732708, 0.7363107781851077, 0.7483099167925688, 0.760854470791278, 0.7845800403105759, 0.7968518866136611, 0.8333947178272924, 0.8453938564347533, 0.8576657027378385,
                0.8702102567365477, 0.8822093953440087, 0.8942085339514697, 0.9064803802545548, 0.9187522265576399, 0.9312967805563492, 0.9430232114681862, 0.9555677654668954, 0.9675669040743565, 1.186823891356144, 1.198823029963605, 1.334631462384414, 1.3583570319037117, 1.3722651243805415, 1.3842642629880026, 1.3962634015954636, 1.4006267247254496, 1.4183527249410168, 1.4270793712009886, 1.4439872483296836, 1.4554409715458962, 1.4682582332402296, 1.5536157419705774, 1.5656148805780385, 1.5781594345767476, 1.5904312808798327, 1.6018850040960455, 1.614702265790379, 1.6267014043978398, 1.6384278353096768, 1.6506996816127621, 1.6626988202202229, 1.6752433742189323, 1.6992416514338542, 1.758419221384287, 1.8195057452040886, 1.9531325160599045, 3.1503192998497647, 3.1631365615440976, 3.1756811155428073, 3.6005597053251766, 3.6120134285413896, 3.6242852748444747, 3.63655712114756, 3.648556259755021, 3.6730999523611914, 3.6970982295761132, 3.7093700758791983, 3.7437312455278366, 3.7557303841352976, 3.7680022304383827, 3.7802740767414678, 3.792545923044553, 3.8053631847388867, 3.817089615650723, 3.829361461953808, 3.89972004742483, 3.9119918937279152, 3.9231729092485037, 3.935444755551589, 3.94744389415905, 3.9591703250708865, 4.047254910757476, 4.071253187972397, 4.183608758569532, 4.41077426902442, 4.472678915931093, 4.4833145160604335, 4.496949900841639, 4.509221747144725, 4.531583778185902, 4.544673747575859, 4.556400178487697, 4.570035563268902, 4.582852824963235, 4.595124671266321, 4.643939348783037, 4.702844211037846, 4.871377566933548, 4.8828312901497615, 4.909829352016549, 4.916647044407151, 4.879558797802272, 4.891557936409733, 5.0014591377462505, 5.013458276353711, 5.025730122656797, 5.037729261264258, 5.074544800173513, 5.50460483617274, 5.517422097867074, 5.929210718259486, 5.9414825645625715, 5.953754410865657, 5.96657167255999, 5.978570811167451, 6.003387211469245, 6.01565905777233, 6.047293150464728, 6.126651089891345, 6.138377520803181]

dataHistoryY = [1468.5, 1438.0, 1430.25, 1465.5, 2843.5, 926.0, 923.75, 921.5, 918.25, 914.5, 915.0, 915.75, 914.75, 909.25, 904.5, 903.25, 900.5, 898.75, 895.25, 292.0, 290.75, 291.0, 292.0, 3190.5, 3176.75, 3297.0, 3306.0, 3333.25, 3342.75, 3366.5, 1375.0, 1352.0, 1352.0, 1932.25, 2025.75, 2003.0, 1994.5, 1993.25, 2002.5, 1939.5, 1949.25, 1286.5, 1814.5, 1813.75, 2455.5, 2448.75, 2458.25, 2473.25, 2474.75, 2460.5, 2459.0, 2459.75, 2486.5, 2515.25, 2519.0, 2523.5, 2531.5, 2541.75, 2550.0, 1294.75, 2592.75, 2596.75, 2604.25, 2615.25, 2624.25, 2636.75, 2652.25, 2679.25, 695.25, 690.25, 688.75, 688.25, 691.0, 694.25, 700.0, 713.5, 2877.5, 2909.75, 2926.5, 2949.25, 2977.5, 3000.25, 3000.25, 1559.75, 3098.0, 3169.5, 3229.5, 3255.25, 3287.5, 3326.25, 3361.5, 3386.25, 3418.75, 3464.25, 3535.25, 3596.75, 3694.25, 3636.75,
                3601.75, 3553.75, 3509.5, 3483.25, 3460.25, 3438.75, 3402.75, 3396.0, 3441.25, 3498.75, 3425.75, 3457.75, 299.5, 296.0, 294.0, 292.5, 291.5, 290.75, 291.25, 292.0, 292.75, 294.0, 296.0, 2697.5, 2706.75, 2720.75, 2718.75, 2711.5, 2717.75, 2722.25, 2722.5, 2733.0, 2740.0, 2738.75, 2749.5, 3289.25, 3179.0, 2900.5, 1189.25, 1180.75, 1169.0, 3111.75, 3159.0, 3207.75, 3212.75, 3233.25, 3253.75, 3297.0, 3338.25, 1387.0, 1397.0, 1408.0, 1420.5, 1426.0, 1417.0, 1396.25, 1373.75, 1695.25, 1678.0, 1676.5, 1693.5, 1716.0, 1729.5, 1463.25, 1451.25, 2879.25, 929.75, 916.5, 913.5, 915.25, 914.0, 911.5, 907.25, 904.5, 903.75, 901.5, 899.0, 895.25, 897.5, 292.0, 290.75, 291.0, 292.0, 3195.75, 3183.5, 3301.0, 3294.25, 3333.0, 3342.0, 3363.75, 1371.5, 1361.5, 2018.5, 1998.0, 1987.5, 1987.5, 1993.0, 1930.5, 1943.25, 1287.25, 1811.75, 1811.5]


def remove_close_points(points):
    # Create a new array to store the points that are not within 10 pixels of each other
    new_points = []

    # Iterate over the points in the input array
    for i in points:
        x = i[0]
        y = i[1]
        found = False
        for j in points:
            if(i == j).all():
                continue
            if(((x-j[0])**2 + (y-j[1])**2) < 100000):
                found = True
                break
        if not found:
            new_points.append(i)

    # Return the new array of points
    return np.array(new_points)


def detectWallPlotting():
    keypoints_coord = []
    cartX = []
    cartY = []
    for i in range(len(dataHistoryX)):
        cartX.append(
            dataHistoryY[i] * math.cos(dataHistoryX[i] + math.pi) + 3000)
        cartY.append(
            -dataHistoryY[i] * math.sin(dataHistoryX[i] + math.pi) + 3000)
    original = np.zeros((6000, 6000), dtype=np.uint8)
    original.fill(255)
    for x, y in zip(cartX, cartY):
        # print(x)
        original[int(x)-15:int(x)+15, int(y)-15:int(y)+15] = 0

    original[3000:, :] = 255

    cv.imshow("img", original)

    params = cv.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 10
    params.maxThreshold = 200

    # Filter by Area.
    params.filterByArea = True
    params.minArea = 2

    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.01

    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.05

    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01

    detector = cv.SimpleBlobDetector_create(params)

    # print(dir(detector))

    # Detect blobs.
    keypoints = detector.detect(original)

    print(keypoints)

    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob

    for point in keypoints:
        keypoints_coord.append([point.pt[0], point.pt[1]])

    keypoints_coord = np.array(keypoints_coord)
    print(keypoints_coord)
    final_keypoints = remove_close_points(keypoints_coord)

    for i in final_keypoints:
        cv.circle(original, (int(i[0]), int(i[1])), 100, (0, 0, 255), 5)

    cv.imshow("A", original)

    cv.waitKey(0)

    # Go through the array and check for poles.
    return original


detectWallPlotting()
# Change the data
# We tell it that the robot has moved forward (up)
