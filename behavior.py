"""
@Time : 2022/2/11 12:00
@Author : guanghao zhou
@File : behavior.py
"""
import numpy as np


class Behavior:
    """
    车辆行为检测
    """

    def __init__(self):
        self.id_memory = set()

    def get_illegal_parking(self, id_tracker):
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
                    if id_ not in self.id_memory:
                        self.id_memory.add(id_)
                        print("id: {}: var_X:{}, var_y:{}".format(id_, x_var, y_var))
                        # print(id_memory)
                    if id_ not in self.id_memory:
                        pass

    def get_retrograde(self):
        pass
