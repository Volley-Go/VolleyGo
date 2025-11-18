"""
视频处理模块 - 提取关键帧
"""
import cv2
import numpy as np
import tempfile
import os


class VideoProcessor:
    def __init__(self):
        pass
    
    def extract_key_frame(self, video_path, method='middle'):
        """
        提取视频关键帧
        
        Args:
            video_path: 视频文件路径
            method: 提取方法
                - 'middle': 提取中间帧
                - 'motion': 提取运动最剧烈的帧
                - 'all': 提取所有帧
                
        Returns:
            frame(s): 提取的帧
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频: {video_path}")
        
        # 获取视频信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if method == 'middle':
            # 提取中间帧
            middle_frame_idx = total_frames // 2
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_idx)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return frame
            else:
                raise ValueError("无法读取中间帧")
        
        elif method == 'motion':
            # 提取运动最剧烈的帧
            frames = []
            frame_diffs = []
            prev_frame = None
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frames.append(frame)
                
                # 计算帧差
                if prev_frame is not None:
                    diff = cv2.absdiff(
                        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                        cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                    )
                    frame_diffs.append(np.sum(diff))
                else:
                    frame_diffs.append(0)
                
                prev_frame = frame
            
            cap.release()
            
            if len(frames) == 0:
                raise ValueError("视频中没有有效帧")
            
            # 找到运动最剧烈的帧
            max_diff_idx = int(np.argmax(frame_diffs))  # 转换为Python int
            return frames[max_diff_idx]
        
        elif method == 'all':
            # 提取所有帧（每秒取2帧）
            frames = []
            frame_interval = max(1, int(fps / 2))
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frames.append(frame)
                
                frame_count += 1
            
            cap.release()
            return frames
        
        else:
            cap.release()
            raise ValueError(f"未知的提取方法: {method}")
    
    def save_uploaded_file(self, uploaded_file):
        """
        保存Streamlit上传的文件到临时目录
        
        Args:
            uploaded_file: Streamlit的UploadedFile对象
            
        Returns:
            temp_path: 临时文件路径
        """
        # 创建临时文件
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        # 保存文件
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.read())
        
        return temp_path
    
    def get_video_info(self, video_path):
        """获取视频信息"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        info = {
            'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
        }
        
        cap.release()
        return info

