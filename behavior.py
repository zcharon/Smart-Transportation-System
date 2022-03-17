"""
@Time : 2022/2/11 12:00
@Author : guanghao zhou
@File : behavior.py
"""
import cv2
import numpy as np
import time
from scipy import stats as st
import math


def get_illegal_parking(id_tracker, id_dirt):
    """
    进行车辆违停检测
    """
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


def __get_angle(v1, v2):
    """
    求两个向量的夹角
    """
    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]
    dx2 = v2[2] - v2[0]
    dy2 = v2[3] - v2[1]
    angle1 = math.atan2(dy1, dx1)  # 返回向量1的弧度值
    angle2 = math.atan2(dy2, dx2)  # 返回向量2的弧度制
    if angle1 * angle2 >= 0:  # 如果两个向量角度同号
        included_angle = abs(angle1 - angle2)
    else:  # 如果两个向量角度异号
        included_angle = abs(angle1) + abs(angle2)
    if included_angle > math.pi:
        included_angle = 2 * math.pi - included_angle
    return included_angle


def get_retrograde(id_tracker, retrograde_tracker=None, start_point=(0, 0), end_point=(0, 0), slope=None):
    """
    进行车辆逆行检测
    计算鼠标绘制向量与车辆轨迹向量的夹角，
    """
    if retrograde_tracker is None:
        retrograde_tracker = {}
    now_set = set()
    add_dirt = {}
    # mem_set = set(retrograde_tracker.keys())
    if slope is None:
        pass  # 直线斜率
    x = []
    y = []
    # 如果当前ID所保存的轨迹点的数量大于10，则进行逆行检测
    # 求每辆车的行驶轨迹的拟合向量，并求该拟合向量的斜率
    for key, tracker in id_tracker.items():
        if len(tracker) > 15:
            for item in tracker:
                x.append(item[0])
                y.append(item[1])
            slope_lin, intercept_lin, _, _, _ = st.linregress(x, y)
            # 使用拟合直线计算预测向量，计算两个向量的夹角，从而判断该车辆是否逆向行驶
            start_point_line = [tracker[0][0], tracker[0][0] * slope_lin + intercept_lin]
            end_point_line = [tracker[-1][0], tracker[-1][0] * slope_lin + intercept_lin]
            angle = __get_angle([start_point[0], start_point[1], end_point[0], end_point[1]],
                                [start_point_line[0], start_point_line[1], end_point_line[0], end_point_line[1]])
            if angle > math.pi / 4:  # 如果车辆行驶
                now_set.add(key)
                # print('SET ADD', now_set)
                if key not in retrograde_tracker:
                    retrograde_tracker[key] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    add_dirt[key] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    # print("SET: ", now_set)
    return retrograde_tracker, add_dirt


class Count:
    """
    车辆计数类
    """

    def __init__(self):
        # list与蓝色框重叠
        self.list_overlapping_blue_polygon = []
        # list与黄色polygon重叠
        self.list_overlapping_yellow_polygon = []
        # 图片尺寸
        self.height = 0
        self.width = 0
        # 车流量计数
        self.down_count = 0
        self.up_count = 0
        # 车流量计数线基准点
        self.point_1 = ()
        self.point_2 = ()
        # list与蓝色polygon重叠
        self.list_overlapping_blue_polygon = []
        # list 与黄色polygon重叠
        self.list_overlapping_yellow_polygon = []

    def __draw_mask(self):
        # 根据视频尺寸，填充一个polygon，供撞线计算使用
        mask_image_temp = np.zeros((self.height, self.width), dtype=np.uint8)
        # 初始化2个撞线polygon  蓝色
        # 蓝色多边形坐标，可根据自己的场景修改
        list_pts_blue = [[self.point_1[0], self.point_1[1] - 20], [self.point_2[0], self.point_2[1] - 20],
                         [self.point_2[0], self.point_2[1]], [self.point_1[0], self.point_1[1]]]
        ndarray_pts_blue = np.array(list_pts_blue, np.int32)
        polygon_blue_value_1 = cv2.fillPoly(mask_image_temp, [ndarray_pts_blue], color=1)  # 构建多边形
        polygon_blue_value_1 = polygon_blue_value_1[:, :, np.newaxis]
        # 填充第二个polygon    黄色
        mask_image_temp = np.zeros((self.height, self.width), dtype=np.uint8)
        # 黄色多边形坐标，可根据自己的场景修改
        list_pts_yellow = [[self.point_1[0], self.point_1[1] + 20], [self.point_2[0], self.point_2[1] + 20],
                           [self.point_2[0], self.point_2[1]], [self.point_1[0], self.point_1[1]]]
        ndarray_pts_yellow = np.array(list_pts_yellow, np.int32)
        polygon_yellow_value_2 = cv2.fillPoly(mask_image_temp, [ndarray_pts_yellow], color=2)  # 构建多边形
        polygon_yellow_value_2 = polygon_yellow_value_2[:, :, np.newaxis]
        # 撞线检测用mask，包含2个polygon，（值范围 0、1、2），供撞线计算使用

        polygon_mask_blue_and_yellow = polygon_blue_value_1 + polygon_yellow_value_2
        # 缩小尺寸，1920x1080->960x540
        polygon_mask_blue_and_yellow = cv2.resize(polygon_mask_blue_and_yellow, (self.width, self.height))
        return polygon_mask_blue_and_yellow

    def count_car(self, frame, list_bboxs):
        if self.width <= 0 or self.height <= 0:
            return frame, 0, 0
        # 根据视频尺寸，填充供撞线计算使用的polygon
        polygon_mask_blue_and_yellow = self.__draw_mask()
        cv2.line(frame, self.point_1, self.point_2, (138, 43, 226), 4)
        if len(list_bboxs) > 0:
            # ----------------------判断撞线----------------------
            for item_bbox in list_bboxs:
                x1, y1, x2, y2, _, track_id = item_bbox
                # 撞线检测点，(x1，y1)，y方向偏移比例 0.0~1.0
                y1_offset = int(y1 + ((y2 - y1) * 0.6))
                # 撞线的点
                y = y1_offset
                x = x1
                if polygon_mask_blue_and_yellow[y, x] == 1:
                    # 如果撞 蓝polygon
                    if track_id not in self.list_overlapping_blue_polygon:
                        self.list_overlapping_blue_polygon.append(track_id)
                    # 判断 黄polygon list里是否有此 track_id
                    # 有此track_id，则认为是 UP (上行)方向
                    if track_id in self.list_overlapping_yellow_polygon:
                        # 上行+1
                        self.up_count += 1
                        print('up count:', self.up_count, ', up id:', self.list_overlapping_yellow_polygon)
                        # 删除 黄polygon list 中的此id
                        self.list_overlapping_yellow_polygon.remove(track_id)

                if polygon_mask_blue_and_yellow[y, x] == 2:
                    # 如果撞 黄polygon
                    if track_id not in self.list_overlapping_yellow_polygon:
                        self.list_overlapping_yellow_polygon.append(track_id)
                    # 判断 蓝polygon list 里是否有此 track_id
                    # 有此 track_id，则 认为是 DOWN（下行）方向
                    if track_id in self.list_overlapping_blue_polygon:
                        # 下行+1
                        self.down_count += 1
                        print('down count:', self.down_count, ', down id:', self.list_overlapping_blue_polygon)
                        # 删除 蓝polygon list 中的此id
                        self.list_overlapping_blue_polygon.remove(track_id)
            # ----------------------清除无用id----------------------
            list_overlapping_all = self.list_overlapping_yellow_polygon + self.list_overlapping_blue_polygon
            for id1 in list_overlapping_all:
                is_found = False
                for _, _, _, _, _, bbox_id in list_bboxs:
                    if bbox_id == id1:
                        is_found = True
                if not is_found:
                    # 如果没找到，删除id
                    if id1 in self.list_overlapping_yellow_polygon:
                        self.list_overlapping_yellow_polygon.remove(id1)

                    if id1 in self.list_overlapping_blue_polygon:
                        self.list_overlapping_blue_polygon.remove(id1)
            list_overlapping_all.clear()
            # 清空list
            list_bboxs.clear()
        else:
            # 如果图像中没有任何的bbox，则清空list
            self.list_overlapping_blue_polygon.clear()
            self.list_overlapping_yellow_polygon.clear()

        # # 输出计数信息
        # text_draw = 'DOWN: ' + str(self.down_count) + ' , UP: ' + str(self.up_count)
        # frame = cv2.putText(img=frame, text=text_draw,
        #                     org=draw_text_postion,
        #                     fontFace=font_draw_number,
        #                     fontScale=0.75, color=(0, 0, 255), thickness=2)
        return frame, self.up_count, self.down_count
