"""
排球动作识别API接口
为前端提供标准化的接口
"""
import os
import sys
from pathlib import Path
import tempfile
import cv2
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.services import VolleyballService
from config.settings import OUTPUT_DIR


class VolleyballAPI:
    """排球动作识别API类"""
    
    def __init__(self):
        """初始化API"""
        self.service = VolleyballService()
    
    def analyze_uploaded_video(self, uploaded_file, analysis_mode="single"):
        """
        分析上传的视频文件
        
        Args:
            uploaded_file: Streamlit上传的文件对象
            analysis_mode: 分析模式 ("single" 或 "sequence")
            
        Returns:
            dict: 分析结果
        """
        # 保存上传的文件到临时目录
        temp_path = self._save_uploaded_file(uploaded_file)
        
        try:
            # 调用服务层分析视频
            result = self.service.analyze_video(temp_path, mode=analysis_mode)
            return result
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    def analyze_image(self, image):
        """
        分析单张图像
        
        Args:
            image: 图像数据（numpy array或PIL Image）
            
        Returns:
            dict: 分析结果
        """
        # 如果是PIL Image，转换为numpy array
        if hasattr(image, 'convert'):
            image = np.array(image.convert('RGB'))
        
        # 调用服务层分析图像
        return self.service.analyze_single_frame(image)
    
    def generate_visualization(self, uploaded_file, vis_type="overlay",
                               detect_ball=False, highlight_ball=False):
        """
        生成可视化视频
        
        Args:
            uploaded_file: 上传的视频文件
            vis_type: 可视化类型
            detect_ball: 是否启用排球检测
            highlight_ball: 是否在输出中绘制排球标记
            
        Returns:
            tuple: (success: bool, output_path: str, error: str)
        """
        # 保存上传的文件
        temp_input_path = self._save_uploaded_file(uploaded_file)
        
        # 生成输出文件路径
        output_filename = f"vis_{vis_type}_{uploaded_file.name}"
        output_path = OUTPUT_DIR / output_filename
        
        try:
            # 调用服务层生成可视化
            result = self.service.generate_visualization_video(
                video_path=str(temp_input_path),
                output_path=str(output_path),
                vis_type=vis_type,
                detect_ball=detect_ball,
                highlight_ball=highlight_ball
            )
            
            if result["success"]:
                return True, str(output_path), None
            else:
                return False, None, result.get("error", "未知错误")
                
        except Exception as e:
            return False, None, str(e)
        finally:
            # 清理临时文件
            if os.path.exists(temp_input_path):
                try:
                    os.remove(temp_input_path)
                except:
                    pass
    
    def get_score_summary(self, score_result):
        """
        获取评分摘要信息
        
        Args:
            score_result: 评分结果字典
            
        Returns:
            dict: 摘要信息
        """
        if not score_result:
            return None
        
        total_score = score_result.get("total_score", 0)
        
        return {
            "total_score": total_score,
            "arm_score": score_result.get("arm_score", 0),
            "body_score": score_result.get("body_score", 0),
            "position_score": score_result.get("position_score", 0),
            "stability_score": score_result.get("stability_score", 0),
            "level_info": self.service.get_level_info(total_score),
            "feedback": self.service.get_feedback_messages(score_result)
        }
    
    def extract_key_frame(self, uploaded_file, method='motion'):
        """
        提取视频关键帧
        
        Args:
            uploaded_file: 上传的视频文件
            method: 提取方法
            
        Returns:
            numpy.ndarray: 关键帧图像
        """
        temp_path = self._save_uploaded_file(uploaded_file)
        
        try:
            frame = self.service.video_processor.extract_key_frame(
                temp_path, 
                method=method
            )
            return frame
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    def _save_uploaded_file(self, uploaded_file):
        """
        保存上传的文件到临时目录
        
        Args:
            uploaded_file: Streamlit的UploadedFile对象
            
        Returns:
            str: 临时文件路径
        """
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.read())
        
        # 重置文件指针，以便后续可以再次读取
        uploaded_file.seek(0)
        
        return temp_path
    
    @staticmethod
    def validate_video_file(uploaded_file, max_size_mb=50):
        """
        验证视频文件
        
        Args:
            uploaded_file: 上传的文件
            max_size_mb: 最大文件大小（MB）
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        # 检查文件扩展名
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        
        if file_ext not in valid_extensions:
            return False, f"不支持的文件格式。请上传 {', '.join(valid_extensions)} 格式的视频。"
        
        # 检查文件大小
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"文件太大（{file_size_mb:.1f}MB）。请上传小于 {max_size_mb}MB 的视频。"
        
        return True, None

