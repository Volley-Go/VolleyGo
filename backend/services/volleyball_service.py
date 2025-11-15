"""
排球动作识别服务
整合核心功能，提供高层业务逻辑
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.core import (
    PoseDetector, 
    VideoProcessor, 
    VolleyballScorer,
    SequenceAnalyzer,
    TrajectoryVisualizer,
    VideoGenerator
)
from backend.core.scorer_v2 import VolleyballScorerV2
from config.settings import TEMPLATES_DIR, DEFAULT_TEMPLATE


class VolleyballService:
    """排球动作识别服务类"""
    
    def __init__(self, use_v2_scorer=True):
        """初始化服务
        
        Args:
            use_v2_scorer: 是否使用优化版评分器（默认True）
        """
        self.pose_detector = PoseDetector()
        self.video_processor = VideoProcessor()
        
        # 使用新的模板路径
        template_path = TEMPLATES_DIR / "default_template.json"
        if not template_path.exists():
            # 如果不存在，使用旧路径兼容
            template_path = Path("template.json")
        
        # 选择评分器版本
        if use_v2_scorer:
            self.scorer = VolleyballScorerV2(template_path=str(template_path))
            print("✅ 使用优化版评分系统 V2")
        else:
            self.scorer = VolleyballScorer(template_path=str(template_path))
        
        self.sequence_analyzer = SequenceAnalyzer()
        self.trajectory_visualizer = TrajectoryVisualizer()
        self.video_generator = VideoGenerator()
        self.use_v2_scorer = use_v2_scorer
    
    def analyze_single_frame(self, image):
        """
        分析单帧图像
        
        Args:
            image: 图像数据（numpy array）
            
        Returns:
            dict: 分析结果，包含：
                - landmarks: 关键点数据
                - score: 评分结果
                - pose_image: 标注后的图像
        """
        try:
            # 检测姿态（返回tuple: landmarks, annotated_image）
            landmarks, pose_image = self.pose_detector.detect_pose(image)
            
            if landmarks is None:
                return {
                    "success": False,
                    "error": "未检测到人体姿态",
                    "landmarks": None,
                    "score": None,
                    "pose_image": image
                }
            
            # 评分
            score_result = self.scorer.score_pose(landmarks)
            
            return {
                "success": True,
                "landmarks": landmarks,
                "score": score_result,
                "pose_image": pose_image
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"分析失败: {str(e)}",
                "landmarks": None,
                "score": None,
                "pose_image": image
            }
    
    def analyze_video(self, video_path, mode="single"):
        """
        分析视频
        
        Args:
            video_path: 视频文件路径
            mode: 分析模式
                - "single": 单帧分析（提取关键帧）
                - "sequence": 序列分析（连续帧）
                
        Returns:
            dict: 分析结果
        """
        if mode == "single":
            return self._analyze_video_single_frame(video_path)
        elif mode == "sequence":
            return self._analyze_video_sequence(video_path)
        else:
            return {
                "success": False,
                "error": f"未知的分析模式: {mode}"
            }
    
    def _analyze_video_single_frame(self, video_path):
        """单帧模式分析视频"""
        try:
            # 提取关键帧
            key_frame = self.video_processor.extract_key_frame(
                video_path, 
                method='motion'
            )
            
            # 分析关键帧
            result = self.analyze_single_frame(key_frame)
            result["video_info"] = self.video_processor.get_video_info(video_path)
            result["analysis_mode"] = "single_frame"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"视频分析失败: {str(e)}"
            }
    
    def _analyze_video_sequence(self, video_path):
        """序列模式分析视频"""
        try:
            # 使用序列分析器
            analysis_result = self.sequence_analyzer.analyze_sequence(video_path)
            
            if not analysis_result.get("success", False):
                return analysis_result
            
            # 获取关键点序列
            frames_data = analysis_result.get("frames_data", [])
            landmarks_sequence = [frame.get("landmarks") for frame in frames_data if frame.get("landmarks")]
            
            # 如果使用V2评分器，进行序列评分
            if self.use_v2_scorer and len(landmarks_sequence) > 0:
                # 使用V2的序列评分功能
                sequence_score_result = self.scorer.score_sequence(landmarks_sequence)
                
                # 获取最佳帧的分项得分
                best_frame_idx = sequence_score_result.get('best_frame_idx', 0)
                if best_frame_idx < len(landmarks_sequence):
                    best_landmarks = landmarks_sequence[best_frame_idx]
                    if best_landmarks:
                        # 获取最佳帧的详细分项得分
                        best_frame_detail = self.scorer.score_pose(best_landmarks)
                        arm_score = best_frame_detail.get('arm_score', 0)
                        body_score = best_frame_detail.get('body_score', 0)
                        position_score = best_frame_detail.get('position_score', 0)
                        stability_score = best_frame_detail.get('stability_score', 0)
                    else:
                        arm_score = body_score = position_score = stability_score = 0
                else:
                    arm_score = body_score = position_score = stability_score = 0
                
                analysis_result["score"] = {
                    'total_score': sequence_score_result['total_score'],
                    'arm_score': arm_score,
                    'body_score': body_score,
                    'position_score': position_score,
                    'stability_score': stability_score,
                    'feedback': sequence_score_result.get('feedback', [])
                }
                analysis_result["sequence_scores"] = {
                    'smoothness': sequence_score_result.get('smoothness', 0) * 100,
                    'completeness': sequence_score_result.get('completeness', 0) * 100,
                    'consistency': sequence_score_result.get('best_frame_score', 0)
                }
            else:
                # 使用旧版单帧评分
                best_frame_idx = analysis_result.get("best_frame_idx", 0)
                
                if frames_data and best_frame_idx < len(frames_data):
                    best_frame_data = frames_data[best_frame_idx]
                    landmarks = best_frame_data.get("landmarks")
                    
                    if landmarks:
                        # 对最佳帧进行评分
                        score_result = self.scorer.score_pose(landmarks)
                        analysis_result["score"] = score_result
            
            # 获取姿态图像
            annotated_frames = analysis_result.get("annotated_frames", [])
            if annotated_frames and best_frame_idx < len(annotated_frames):
                analysis_result["pose_image"] = annotated_frames[best_frame_idx]
            
            # 生成轨迹可视化
            trajectories = analysis_result.get("trajectories", {})
            if trajectories:
                trajectory_plot = self.trajectory_visualizer.create_trajectory_plot(
                    trajectories
                )
                analysis_result["trajectory_plot"] = trajectory_plot
            
            # 添加序列评分（如果有）
            if "smoothness_score" in analysis_result:
                analysis_result["sequence_scores"] = {
                    "smoothness": analysis_result.get("smoothness_score", 0),
                    "completeness": analysis_result.get("completeness_score", 0),
                    "consistency": analysis_result.get("consistency_score", 0)
                }
            
            analysis_result["analysis_mode"] = "sequence"
            analysis_result["video_info"] = self.video_processor.get_video_info(video_path)
            
            return analysis_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"序列分析失败: {str(e)}"
            }
    
    def generate_visualization_video(self, video_path, output_path, vis_type="overlay",
                                     detect_ball=False, highlight_ball=False):
        """
        生成可视化视频
        
        Args:
            video_path: 原始视频路径
            output_path: 输出视频路径
            vis_type: 可视化类型
                - "overlay": 骨架叠加
                - "skeleton": 纯骨架
                - "comparison": 对比视频
                - "trajectory": 轨迹追踪
                
        Returns:
            dict: 生成结果
        """
        try:
            self.video_generator.generate_video(
                video_path=video_path,
                output_path=output_path,
                video_type=vis_type,
                detect_ball=detect_ball,
                highlight_ball=highlight_ball
            )
            
            return {
                "success": True,
                "output_path": output_path,
                "video_type": vis_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"视频生成失败: {str(e)}"
            }
    
    def get_feedback_messages(self, score_result):
        """
        根据评分结果生成反馈消息
        
        Args:
            score_result: 评分结果字典
            
        Returns:
            list: 反馈消息列表
        """
        feedback = score_result.get("feedback", [])
        total_score = score_result.get("total_score", 0)
        
        # 添加总体评价
        if total_score >= 85:
            overall = "🎉 优秀！动作标准，继续保持！"
        elif total_score >= 60:
            overall = "👍 良好！还有提升空间。"
        else:
            overall = "💪 需要改进，加油练习！"
        
        return [overall] + feedback
    
    def get_level_info(self, total_score):
        """
        根据分数获取关卡信息
        
        Args:
            total_score: 总分
            
        Returns:
            dict: 关卡信息
        """
        if total_score >= 85:
            return {
                "level": "advanced",
                "level_name": "高级",
                "passed": True,
                "next_level": None,
                "message": "🏆 恭喜！你已达到专业水平！"
            }
        elif total_score >= 70:
            return {
                "level": "intermediate",
                "level_name": "中级",
                "passed": True,
                "next_level": "advanced",
                "message": "🌟 很好！向高级关卡进发！"
            }
        elif total_score >= 50:
            return {
                "level": "beginner",
                "level_name": "初级",
                "passed": True,
                "next_level": "intermediate",
                "message": "✨ 通过初级关卡！继续努力！"
            }
        else:
            return {
                "level": "beginner",
                "level_name": "初级",
                "passed": False,
                "next_level": "beginner",
                "message": "📚 继续练习基础动作！"
            }

