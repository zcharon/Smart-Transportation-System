from collections import deque
from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort

import torch
import cv2

palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)
cfg = get_config()
cfg.merge_from_file("deep_sort/configs/deep_sort.yaml")
deepsort = DeepSort(cfg.DEEPSORT.REID_CKPT,
                    max_dist=cfg.DEEPSORT.MAX_DIST, min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
                    nms_max_overlap=cfg.DEEPSORT.NMS_MAX_OVERLAP, max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                    max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                    use_cuda=True)


def draw_track(image, veh_id_old, bboxes):
    """
    绘制轨迹点
    """
    veh_id_new = {}
    for (x1, y1, x2, y2, cls_id, pos_id) in bboxes:
        veh_id_new[pos_id] = (int((x1 + x2) / 2), int((y1 + y2) / 2))
    id_new = set(veh_id_new.keys())  # 新检测帧中的所有id号
    id_old = set(veh_id_old.keys())  # 旧检测帧中的所有id号
    id_union = id_new | id_old
    id_diff = id_union - id_new
    id_union_new = id_union - id_diff
    for i in id_diff:  # 删除不存在的id及其轨迹点
        veh_id_old.pop(i)
    for i in id_union_new:
        if i in veh_id_old:
            veh_id_old[i].append(veh_id_new[i])
            if len(veh_id_old[i]) > 80:
                veh_id_old[i].popleft()
        else:
            veh_id_old[i] = deque([veh_id_new[i]])

    for values in veh_id_old.values():
        for point in values:
            cv2.circle(image, (point[0], point[1]), 5, (0, 0, 255), -1)
    return image, veh_id_old


def plot_bboxes(image, bboxes, id_tracker, line_thickness=None):
    """
    绘制检测后的图像
    """
    # Plots one bounding box on image img
    tl = line_thickness or round(
        0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness

    image, id_tracker = draw_track(image, id_tracker, bboxes)
    for (x1, y1, x2, y2, cls_id, pos_id) in bboxes:
        if cls_id in ['person']:
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)
        c1, c2 = (x1, y1), (x2, y2)
        cv2.rectangle(image, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(cls_id, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(image, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(image, '{} ID-{}'.format(cls_id, pos_id), (c1[0], c1[1] - 2), 0, tl / 3,
                    [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

    return image, id_tracker


def update_tracker(target_detector, image, id_tracker):
    """
    更新预测轨迹
    """
    new_vehicle = []
    _, bboxes = target_detector.detect(image)

    bbox_xywh = []
    confs = []
    clss = []
    if len(bboxes):
        for x1, y1, x2, y2, cls_id, conf in bboxes:
            obj = [
                int((x1 + x2) / 2), int((y1 + y2) / 2),
                x2 - x1, y2 - y1
            ]
            bbox_xywh.append(obj)
            confs.append(conf)
            clss.append(cls_id)

        xywhs = torch.Tensor(bbox_xywh)
        confss = torch.Tensor(confs)
        outputs = deepsort.update(xywhs, confss, clss, image)

        bboxes2draw = []
        list_boxes = []
        current_ids = []
        for value in list(outputs):
            x1, y1, x2, y2, cls_, track_id = value
            bboxes2draw.append(
                (x1, y1, x2, y2, cls_, track_id)
            )
            current_ids.append(track_id)
            if cls_ == 'person' or cls_ == 'car' or cls_ == 'truck':
                if not track_id in target_detector.tracker:
                    target_detector.tracker[track_id] = 0
                    face = image[y1:y2, x1:x2]
                    new_vehicle.append((face, track_id))
                list_boxes.append(
                    (x1, y1, x2, y2, cls_, track_id)
                )

        ids2delete = []
        for history_id in target_detector.tracker:
            if not history_id in current_ids:
                target_detector.tracker[history_id] -= 1
            if target_detector.tracker[history_id] < -5:
                ids2delete.append(history_id)

        for ids in ids2delete:
            target_detector.tracker.pop(ids)
            # print('-[INFO] Delete track id:', ids)

        image, id_tracker = plot_bboxes(image, bboxes2draw, id_tracker)
        return image, new_vehicle, list_boxes, id_tracker

    return image, [], [], id_tracker
