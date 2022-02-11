"""
@Time : 2022/2/10 13:58
@Author : guanghao zhou
@File : count_car_.py
"""
import numpy as np
import cv2


class Count:
    def __init__(self):
        # list 与蓝色框重叠
        self.list_overlapping_blue_polygon = []
        # list 与黄色polygon重叠
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
        list_pts_blue = [[self.point_1[0], self.point_1[1] - 40], [self.point_2[0], self.point_2[1] - 40],
                         [self.point_2[0], self.point_2[1]], [self.point_1[0], self.point_1[1]]]
        ndarray_pts_blue = np.array(list_pts_blue, np.int32)
        polygon_blue_value_1 = cv2.fillPoly(mask_image_temp, [ndarray_pts_blue], color=1)  # 构建多边形
        polygon_blue_value_1 = polygon_blue_value_1[:, :, np.newaxis]
        # 填充第二个polygon    黄色
        mask_image_temp = np.zeros((self.height, self.width), dtype=np.uint8)
        # 黄色多边形坐标，可根据自己的场景修改
        list_pts_yellow = [[self.point_1[0], self.point_1[1] + 40], [self.point_2[0], self.point_2[1] + 40],
                           [self.point_2[0], self.point_2[1]], [self.point_1[0], self.point_1[1]]]
        ndarray_pts_yellow = np.array(list_pts_yellow, np.int32)
        polygon_yellow_value_2 = cv2.fillPoly(mask_image_temp, [ndarray_pts_yellow], color=2)  # 构建多边形
        polygon_yellow_value_2 = polygon_yellow_value_2[:, :, np.newaxis]
        # 撞线检测用mask，包含2个polygon，（值范围 0、1、2），供撞线计算使用

        polygon_mask_blue_and_yellow = polygon_blue_value_1 + polygon_yellow_value_2
        # 缩小尺寸，1920x1080->960x540
        polygon_mask_blue_and_yellow = cv2.resize(polygon_mask_blue_and_yellow, (self.width, self.height))
        # 蓝 色盘 b,g,r
        blue_color_plate = [255, 0, 0]
        # 蓝 polygon图片
        blue_image = np.array(polygon_blue_value_1 * blue_color_plate, np.uint8)

        # 黄 色盘
        yellow_color_plate = [0, 255, 255]
        # 黄 polygon图片
        yellow_image = np.array(polygon_yellow_value_2 * yellow_color_plate, np.uint8)

        # 彩色图片（值范围 0-255）
        color_polygons_image = blue_image + yellow_image
        # 缩小尺寸，1920x1080->960x540
        color_polygons_image = cv2.resize(color_polygons_image, (self.width, self.height))

        return polygon_mask_blue_and_yellow, color_polygons_image

    def count_car(self, frame, list_bboxs):
        if self.width <= 0 or self.height <= 0:
            return frame, 0, 0
        # 根据视频尺寸，填充供撞线计算使用的polygon
        polygon_mask_blue_and_yellow, color_polygons_image = self.__draw_mask()
        font_draw_number = cv2.FONT_HERSHEY_SIMPLEX
        draw_text_postion = (int((self.width / 2.0) * 0.01), int((self.height / 2.0) * 0.05))
        frame = cv2.add(frame, color_polygons_image)
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

<<<<<<< HEAD
        # 输出计数信息
        text_draw = 'DOWN: ' + str(self.down_count) + ' , UP: ' + str(self.up_count)
        frame = cv2.putText(img=frame, text=text_draw,
                            org=draw_text_postion,
                            fontFace=font_draw_number,
                            fontScale=0.75, color=(0, 0, 255), thickness=2)
=======
        # # 输出计数信息
        # text_draw = 'DOWN: ' + str(self.down_count) + ' , UP: ' + str(self.up_count)
        # frame = cv2.putText(img=frame, text=text_draw,
        #                     org=draw_text_postion,
        #                     fontFace=font_draw_number,
        #                     fontScale=0.75, color=(0, 0, 255), thickness=2)
>>>>>>> f25945e (1.修改count_car使车流量统计数据在GUI中显示而不在frame中显示)
        return frame, self.up_count, self.down_count
