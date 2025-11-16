"""
排球检测模块 - 使用MediaPipe Tasks识别视频帧中的排球
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np
import mediapipe as mp

# from config.settings import MODELS_DIR


try:
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
except ImportError as exc:  # pragma: no cover - 仅在环境缺少tasks模块时触发
    raise ImportError(
        "MediaPipe Tasks API 未安装，无法使用排球检测功能。"
    ) from exc


DEFAULT_MODEL_NAME = "efficientdet_lite0.tflite"


@dataclass
class VolleyballDetection:
    """排球检测结果结构体"""

    label: str
    score: float
    bbox: Tuple[int, int, int, int]
    bbox_normalized: Tuple[float, float, float, float]

    @property
    def center(self) -> Tuple[float, float]:
        x_min, y_min, x_max, y_max = self.bbox_normalized
        return (x_min + x_max) / 2.0, (y_min + y_max) / 2.0


class VolleyballDetector:
    """
    使用MediaPipe ObjectDetector检测排球
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
            model_path: TFLite检测模型路径（默认data/models/efficientdet_lite0.tflite）
            score_threshold: 置信度阈值
            max_results: 每帧最多返回的检测数量
            target_labels: 允许运动类别列表
        """
        self.model_path = Path(model_path) if model_path else "D:\Code\Projects\AIxVolleyball\data\models\efficientdet_lite0.tflite"
        
        self.score_threshold = score_threshold
        self.max_results = max_results
        self.target_labels = [label.lower() for label in (target_labels or ["volleyball", "sports ball", "ball"])]
        self._detector = None
        self._init_detector()

    def _init_detector(self) -> None:
        # if not self.model_path.exists():
        #     raise FileNotFoundError(
        #         f"未找到排球检测模型: {self.model_path}. "
        #         "请将MediaPipe兼容的TFLite检测模型放置到data/models目录。"
        #     )
        print(f"正在加载排球检测模型: {self.model_path}")
        # base_options = mp_python.BaseOptions(model_asset_path=self.model_path)
        # 用 buffer 读入模型
        with open(self.model_path, "rb") as f:
            model_bytes = f.read()

        base_options = mp_python.BaseOptions(
            model_asset_buffer=model_bytes  # ✅ 用 buffer，不再用路径
        )
        # print("[V_DETECTOR] BaseOptions: ", base_options)
        options = vision.ObjectDetectorOptions(
            base_options=base_options,
            max_results=self.max_results,
            score_threshold=self.score_threshold,
            running_mode=vision.RunningMode.IMAGE,
        )
        # print("[V_DETECTOR] Options: ", options)
        self._detector = vision.ObjectDetector.create_from_options(options)
        
    def detect(self, frame: np.ndarray) -> List[VolleyballDetection]:
        """
        检测单帧中的排球

        Args:
            frame: BGR格式的图像

        Returns:
            该帧的排球检测结果列表
        """
        if frame is None:
            return []

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
        )
        detection_result = self._detector.detect(mp_image)
        return self._parse_detections(detection_result, frame.shape)

    def annotate(self, frame: np.ndarray, detections: Sequence[VolleyballDetection]) -> np.ndarray:
        """
        在图像上绘制检测结果
        """
        if frame is None or not detections:
            return frame

        annotated = frame.copy()
        height, width = annotated.shape[:2]

        for detection in detections:
            x_min, y_min, x_max, y_max = detection.bbox_normalized
            pt1 = (int(x_min * width), int(y_min * height))
            pt2 = (int(x_max * width), int(y_max * height))
            cv2.rectangle(annotated, pt1, pt2, (0, 165, 255), 2)
            label = f"{detection.label}: {detection.score:.2f}"
            cv2.putText(
                annotated,
                label,
                (pt1[0], max(pt1[1] - 5, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 165, 255),
                2,
            )

        return annotated

    def detect_and_annotate(self, frame: np.ndarray) -> Tuple[List[VolleyballDetection], np.ndarray]:
        """
        便捷方法：同时返回检测结果和绘制后的图像
        """
        detections = self.detect(frame)
        annotated = self.annotate(frame, detections) if detections else frame
        return detections, annotated

    def _parse_detections(self, detection_result, frame_shape) -> List[VolleyballDetection]:
        height, width = frame_shape[:2]
        parsed: List[VolleyballDetection] = []

        for detection in detection_result.detections:
            if not detection.categories:
                continue

            category = max(detection.categories, key=lambda c: c.score or 0)
            label = (category.category_name or "").lower()
            if self.target_labels and label not in self.target_labels:
                continue

            bbox = detection.bounding_box
            x_min = max(bbox.origin_x / width, 0.0)
            y_min = max(bbox.origin_y / height, 0.0)
            x_max = min((bbox.origin_x + bbox.width) / width, 1.0)
            y_max = min((bbox.origin_y + bbox.height) / height, 1.0)

            parsed.append(
                VolleyballDetection(
                    label=category.category_name or "volleyball",
                    score=category.score or 0.0,
                    bbox=(
                        int(bbox.origin_x),
                        int(bbox.origin_y),
                        int(bbox.origin_x + bbox.width),
                        int(bbox.origin_y + bbox.height),
                    ),
                    bbox_normalized=(x_min, y_min, x_max, y_max),
                )
            )

        return parsed
