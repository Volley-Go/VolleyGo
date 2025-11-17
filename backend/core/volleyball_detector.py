"""
排球检测模块 - 使用 Roboflow / YOLOv7 识别视频帧中的排球
"""
from __future__ import annotations


from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import sys
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.append(str(CURRENT_DIR))

import os
import cv2
import numpy as np

from roboflow import Roboflow
from .my_utils import RoboYOLO, x_y_w_h, custom  # 来自第一个文件使用的工具

# 默认使用哪种模型：'roboflow' 或 'yolov7'
DEFAULT_BACKEND = "yolov7"

# YOLOv7 本地权重默认路径（可根据你实际项目调整）
DEFAULT_YOLOV7_WEIGHTS = Path(CURRENT_DIR / "yV7-tiny/weights/best.pt")

# Roboflow 项目信息（和第一个文件保持一致）
ROBOFLOW_PROJECT = "volleyball-tracking"
ROBOFLOW_VERSION = 18
# Roboflow API Key 可以放到环境变量中：ROBOFLOW_API_KEY
# 或者你也可以在 _init_detector 里写死


@dataclass
class VolleyballDetection:
    """排球检测结果结构体"""

    label: str
    score: float
    bbox: Tuple[int, int, int, int]               # 像素坐标 (x_min, y_min, x_max, y_max)
    bbox_normalized: Tuple[float, float, float, float]  # 归一化坐标 (0~1)

    @property
    def center(self) -> Tuple[float, float]:
        x_min, y_min, x_max, y_max = self.bbox_normalized
        return (x_min + x_max) / 2.0, (y_min + y_max) / 2.0


class VolleyballDetector:
    """
    使用 Roboflow / YOLOv7 (通过 RoboYOLO 封装) 检测排球
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        score_threshold: float = 0.45,
        max_results: int = 3,
        target_labels: Optional[Sequence[str]] = None,
    ):
        """
        Args:
            model_path: 模型文件路径：
                - 如果使用 YOLOv7，则为 .pt 权重路径（默认为 yV7-tiny/weights/best.pt）。
                - 如果使用 Roboflow，则此参数可以忽略。
            score_threshold: 置信度阈值（对应第一个文件中的 confidence）
            max_results: 每帧最多返回的检测数量（目前逻辑只返回最主要的一个球，但接口保留）
            target_labels: 允许运动类别列表，默认 ["volleyball", "sports ball", "ball"]
        """
        # ✅ 保持原有属性和参数名
        self.model_path = Path(model_path) if model_path else DEFAULT_YOLOV7_WEIGHTS
        self.score_threshold = score_threshold
        self.max_results = max_results
        self.target_labels = [
            label.lower() for label in (target_labels or ["volleyball", "sports ball", "ball"])
        ]

        # 使用哪个后端：'roboflow' 或 'yolov7'
        # 如果你想强制使用 yolov7，可以改成 "yolov7"
        self.backend = DEFAULT_BACKEND

        # 内部实际使用的检测模型（RoboYOLO 封装）
        self._detector: Optional[RoboYOLO] = None

        self._init_detector()

    def _init_detector(self) -> None:
        """
        初始化检测模型，把第一个文件里的模型加载逻辑搬过来：
        - backend == 'roboflow' 时，使用 Roboflow API 远程模型
        - backend == 'yolov7' 时，使用本地 YOLOv7 权重
        """
        print(f"[VolleyballDetector] 初始化后端: {self.backend}")

        if self.backend == "roboflow":
            # 你可以把 api_key 写死在这里，或者用环境变量管理
            api_key = os.environ.get("ROBOFLOW_API_KEY", "INSERT YOUR OWN API_KEY")
            if api_key == "INSERT YOUR OWN API_KEY":
                print(
                    "[VolleyballDetector] 警告: 当前使用的是占位 API Key，请在代码中或环境变量 "
                    "ROBOFLOW_API_KEY 中设置真实的 Roboflow API Key。"
                )

            rf = Roboflow(api_key=api_key)
            project = rf.workspace().project(ROBOFLOW_PROJECT)
            model = project.version(ROBOFLOW_VERSION).model

        elif self.backend == "yolov7":
            # 复用第一个文件里的加载逻辑：custom(path_or_model=...)
            weights_path = str(self.model_path)
            if not os.path.exists(weights_path):
                raise FileNotFoundError(f"未找到 YOLOv7 权重文件: {weights_path}")

            model = custom(path_or_model=weights_path)
            print("[TEST][VolleyballDetector] 模型设备：", next(model.parameters()).device)
            
            # 第一个文件中用 model.conf 控制置信度
            model.conf = float(self.score_threshold)

        else:
            raise ValueError(f"未知后端类型: {self.backend}, 支持 'roboflow' 或 'yolov7'")

        # ✅ 使用第一个文件中的 RoboYOLO 包装器
        #   RoboYOLO(model_name, model, conf)
        self._detector = RoboYOLO(self.backend, model, float(self.score_threshold))
        print("[TEST][VolleyballDetector] 模型加载完成。")

    # ----------------- 对外接口：保持不变 -----------------

    def detect(self, frame: np.ndarray) -> List[VolleyballDetection]:
        """
        检测单帧中的排球
        """
        if frame is None or self._detector is None:
            return []

        height, width = frame.shape[:2]

        # === 调用第一个文件的 YOLO 预测方式 ===
        pred = self._detector.predict(frame)

        # x_y_w_h 返回 (x0, y0, w, h)
        bbox = x_y_w_h(pred, self.backend)
        # print("[TEST][VolleyballDetector][DETECT] bbox(x0,y0,w,h):", bbox)

        # === 无结果 ===
        if not bbox or bbox == (0, 0, 0, 0):
            return []

        x0, y0, w, h = bbox

        # === 修正：转换为 x_min x_max y_min y_max ===
        x_min = int(x0)
        y_min = int(y0)
        x_max = int(x0 + w)
        y_max = int(y0 + h)

        # 边界裁剪
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(width - 1, x_max)
        y_max = min(height - 1, y_max)

        # 如果 box 太小或不合法
        if x_min >= x_max or y_min >= y_max:
            return []

        # === 归一化坐标 ===
        nx_min = x_min / float(width)
        ny_min = y_min / float(height)
        nx_max = x_max / float(width)
        ny_max = y_max / float(height)

        # === YOLO 返回的 pred 里包含 score，你如果需要也可以从 pred 中提取 ===
        label = self.target_labels[0]
        score = 1.0  # 你可以换成 pred 的置信度

        detection = VolleyballDetection(
            label=label,
            score=score,
            bbox=(x_min, y_min, x_max, y_max),
            bbox_normalized=(nx_min, ny_min, nx_max, ny_max),
        )

        return [detection]

    # def detect_batch(
    #     self,
    #     frames: Sequence[np.ndarray],
    # ) -> List[List[VolleyballDetection]]:
    #     """
    #     批量检测：对一组帧做并行预测

    #     Args:
    #         frames: [B, H, W, 3] 的 np.ndarray 列表（B 为帧数）

    #     Returns:
    #         detections_per_frame: 长度为 B 的列表，
    #             每个元素是该帧对应的 VolleyballDetection 列表
    #     """
    #     if not frames or self._detector is None:
    #         return [[] for _ in frames]

    #     print("[TEST][DETECT_BATCH] frames: ", len(frames), frames[0].shape)

    #     # 先保存每一帧的尺寸
    #     sizes = [f.shape[:2] for f in frames]  # [(h, w), ...]

    #     # 调用底层 batch 预测
    #     preds = self._detector.predict_batch(frames)

    #     all_detections: List[List[VolleyballDetection]] = []

    #     for i, ((h, w), frame) in enumerate(zip(sizes, frames)):
    #         # 针对不同 backend 拿到当前帧的 bbox
    #         if self.backend == "yolov7":
    #             # preds 是一个 Detections 对象，preds.pred[i] 是第 i 帧的结果
    #             bbox = x_y_w_h(preds, self.backend, idx=i)
    #         elif self.backend == "roboflow":
    #             # preds 是一个列表，逐帧调用 x_y_w_h
    #             bbox = x_y_w_h(preds[i], self.backend)
    #         else:
    #             bbox = (0, 0, 0, 0)

    #         if not bbox or bbox == (0, 0, 0, 0):
    #             all_detections.append([])
    #             continue

    #         x0, y0, bw, bh = bbox

    #         x_min = int(x0)
    #         y_min = int(y0)
    #         x_max = int(x0 + bw)
    #         y_max = int(y0 + bh)

    #         # 边界裁剪
    #         x_min = max(0, x_min)
    #         y_min = max(0, y_min)
    #         x_max = min(w - 1, x_max)
    #         y_max = min(h - 1, y_max)

    #         if x_min >= x_max or y_min >= y_max:
    #             all_detections.append([])
    #             continue

    #         # 归一化
    #         nx_min = x_min / float(w)
    #         ny_min = y_min / float(h)
    #         nx_max = x_max / float(w)
    #         ny_max = y_max / float(h)

    #         label = self.target_labels[0]
    #         score = 1.0  # 你可以改成从 YOLO/Roboflow 的结果里拿真实 score

    #         det = VolleyballDetection(
    #             label=label,
    #             score=score,
    #             bbox=(x_min, y_min, x_max, y_max),
    #             bbox_normalized=(nx_min, ny_min, nx_max, ny_max),
    #         )
    #         all_detections.append([det])

    #     return all_detections
    def detect_batch(
        self,
        frames: Sequence[np.ndarray],
        max_yolo_batch: int = 64,   # ✅ YOLO 实际 batch 大小
    ) -> List[List[VolleyballDetection]]:
        """
        批量检测：对一组帧做并行预测（内部再切小 batch）

        Args:
            frames: [B, H, W, 3] 的 np.ndarray 列表

        Returns:
            detections_per_frame: 长度为 B 的列表，
                每个元素是该帧对应的 VolleyballDetection 列表
        """
        if not frames or self._detector is None:
            return [[] for _ in frames]

        # 先保存每一帧的尺寸
        sizes = [f.shape[:2] for f in frames]  # [(h, w), ...]
        all_detections: List[List[VolleyballDetection]] = []

        # ⚠️ 保证输出顺序和输入一一对应
        num_frames = len(frames)

        import math
        import torch as _torch

        for start in range(0, num_frames, max_yolo_batch):
            print("[TEST][DETECT_BATCH]: processing batch: ", max_yolo_batch)
            end = min(start + max_yolo_batch, num_frames)
            sub_frames = frames[start:end]
            sub_sizes = sizes[start:end]

            # 底层 batch 预测
            preds = self._detector.predict_batch(sub_frames)

            # 对这个小 batch 里的每一帧做后处理
            for j, ((h, w), frame) in enumerate(zip(sub_sizes, sub_frames)):
                if self.backend == "yolov7":
                    # ⚠️ 注意：这里的 idx 现在是小 batch 内部的 j
                    bbox = x_y_w_h(preds, self.backend, idx=j)
                elif self.backend == "roboflow":
                    bbox = x_y_w_h(preds[j], self.backend)
                else:
                    bbox = (0, 0, 0, 0)

                if not bbox or bbox == (0, 0, 0, 0):
                    all_detections.append([])
                    continue

                x0, y0, bw, bh = bbox

                x_min = int(x0)
                y_min = int(y0)
                x_max = int(x0 + bw)
                y_max = int(y0 + bh)

                # 边界裁剪
                x_min = max(0, x_min)
                y_min = max(0, y_min)
                x_max = min(w - 1, x_max)
                y_max = min(h - 1, y_max)

                if x_min >= x_max or y_min >= y_max:
                    all_detections.append([])
                    continue

                # 归一化
                nx_min = x_min / float(w)
                ny_min = y_min / float(h)
                nx_max = x_max / float(w)
                ny_max = y_max / float(h)

                label = self.target_labels[0]
                score = 1.0  # TODO: 需要的话可以从 preds 里拿真实置信度

                det = VolleyballDetection(
                    label=label,
                    score=score,
                    bbox=(x_min, y_min, x_max, y_max),
                    bbox_normalized=(nx_min, ny_min, nx_max, ny_max),
                )
                all_detections.append([det])

            # ✅ 小 batch 结束后，主动释放下 GPU cache（可选，但对长视频挺有用）
            if _torch.cuda.is_available():
                del preds
                _torch.cuda.empty_cache()

        return all_detections
            
    def annotate(
        self,
        frame: np.ndarray,
        detections: Sequence[VolleyballDetection],
        marker: str = "circle",
        color=(0, 165, 255),
        trace: bool = True,
        trace_len: int = 8,
    ) -> np.ndarray:
        """
        在图像上绘制检测结果（支持圆形或矩形标记 + 轨迹绘制）

        Args:
            frame: BGR 图像
            detections: VolleyballDetection 列表
            marker: 'circle' 或 'box'
            color: 绘制颜色 (B, G, R)
            trace: 是否绘制轨迹
            trace_len: 轨迹长度（历史帧的数量）
        """

        if frame is None:
            return frame

        h, w = frame.shape[:2]
        img = frame.copy()

        # ----------------------
        # 初始化轨迹队列（只初始化一次）
        # ----------------------
        if not hasattr(self, "_queue"):
            from collections import deque
            self._queue = deque([None] * trace_len, maxlen=trace_len)

        # ----------------------
        # 1. 读取当前检测框 (若有)
        # ----------------------
        if detections:
            det = detections[0]  # 目前只支持取第1个检测
            x_min, y_min, x_max, y_max = det.bbox_normalized
            cur_box = (
                int(x_min * w),
                int(y_min * h),
                int(x_max * w),
                int(y_max * h),
            )
            self._queue.appendleft(cur_box)
        else:
            self._queue.appendleft(None)

        # ----------------------
        # 2. 绘制轨迹（历史帧）
        # ----------------------
        for i, box in enumerate(self._queue):
            if box is None:
                continue

            x0, y0, x1, y1 = box

            if marker == "box":
                # 历史框画得淡一点
                if i == 0:
                    cv2.rectangle(img, (x0, y0), (x1, y1), color, 2)
                else:
                    cv2.rectangle(img, (x0, y0), (x1, y1), color, 1)

            elif marker == "circle":
                # 计算圆心与半径
                cx = int((x0 + x1) // 2)
                cy = int((y0 + y1) // 2)
                r = int(max((x1 - x0), (y1 - y0)) // 2)

                if i == 0:
                    cv2.circle(img, (cx, cy), r, color, 5)
                else:
                    cv2.circle(img, (cx, cy), max(r - 10, 2), color, -1)

        return img


    def detect_and_annotate(self, frame: np.ndarray) -> Tuple[List[VolleyballDetection], np.ndarray]:
        """
        便捷方法：同时返回检测结果和绘制后的图像
        """
        detections = self.detect(frame)
        annotated = self.annotate(frame, detections) if detections else frame
        return detections, annotated
