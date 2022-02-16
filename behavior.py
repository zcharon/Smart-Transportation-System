"""
@Time : 2022/2/11 12:00
@Author : guanghao zhou
@File : behavior.py
"""
import numpy as np
import time


def get_illegal_parking(id_tracker, id_dirt):
    flag = True
    id_dirt_temp = {}
    for id_, points in id_tracker.items():
        if len(points) > 20:
            x = []
            y = []
            for point in points:
                x.append(point[0])
                y.append(point[1])
            x_var = np.var(x)
            y_var = np.var(y)
            if x_var < 1 and y_var < 1:
                if id_ not in id_dirt:
                    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    id_dirt_temp[id_] = time_str
                    id_dirt[id_] = time_str
                    # print(id_memory)
    return id_dirt_temp, id_dirt


class Behavior:
    """
    车辆行为检测
    """

    def __init__(self):
        self.__ill_parking_id_memory = {}

    def get_retrograde(self):
        pass
