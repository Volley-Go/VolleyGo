"""
视频生成模块 - 生成骨架叠加视频和纯骨架动画
"""
import cv2
import numpy as np
import tempfile
import os
from .pose_detector import PoseDetector


class VideoGenerator:
    """生成骨架视频的类"""
    
    def __init__(self):
        self.detector = PoseDetector()
        # MediaPipe 骨架连接定义
        self.connections = [
            # 躯干
            (11, 12),  # 左肩-右肩
            (11, 23),  # 左肩-左髋
            (12, 24),  # 右肩-右髋
            (23, 24),  # 左髋-右髋
            
            # 左臂
            (11, 13),  # 左肩-左肘
            (13, 15),  # 左肘-左腕
            
            # 右臂
            (12, 14),  # 右肩-右肘
            (14, 16),  # 右肘-右腕
            
            # 左腿
            (23, 25),  # 左髋-左膝
            (25, 27),  # 左膝-左踝
            
            # 右腿
            (24, 26),  # 右髋-右膝
            (26, 28),  # 右膝-右踝
        ]
        
        # 关键点索引映射
        self.landmark_map = {
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_wrist': 15,
            'right_wrist': 16,
            'left_hip': 23,
            'right_hip': 24,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28,
        }
    
    def generate_video(self, video_path, output_path, video_type="overlay", max_frames=600,
                       detect_ball=False, highlight_ball=False):
        """
        统一的视频生成接口
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            video_type: 视频类型
                - "overlay": 骨架叠加
                - "skeleton": 纯骨架
                - "comparison": 左右对比
                - "trajectory": 轨迹追踪
            max_frames: 最大处理帧数（默认300帧，约10-30秒视频）
        
        Returns:
            str: 输出视频路径
        """
        from .sequence_analyzer import SequenceAnalyzer
        import subprocess
        import tempfile
        
        print(f"🎬 开始生成视频: {video_type}")
        
        # 读取视频
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频: {video_path}")
        
        # 获取视频信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 10
        
        print(f"📹 视频信息: {total_frames} 帧, {fps:.1f} FPS")
        
        # 提取帧（限制数量以提高速度）
        frames = []
        frame_count = 0
        
        # 如果帧数太多，进行采样
        if total_frames > max_frames:
            frame_interval = total_frames // max_frames
            print(f"⚡ 帧数过多，每 {frame_interval} 帧采样一次")
        else:
            frame_interval = 1
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frames.append(frame)
                if len(frames) >= max_frames:
                    print(f"⏸️ 已达到最大帧数限制: {max_frames}")
                    break
            
            frame_count += 1
        
        cap.release()
        
        if len(frames) == 0:
            raise ValueError("视频中没有有效帧")
        
        print(f"✅ 提取了 {len(frames)} 帧")
        
        # 分析序列（这是最耗时的部分）
        print("🔍 开始姿态分析...")
        ball_detection_requested = detect_ball or highlight_ball
        analyzer = SequenceAnalyzer(enable_ball_detection=ball_detection_requested)
        sequence_result = analyzer.analyze_sequence(
            frames,
            detect_ball=ball_detection_requested,
            draw_ball=ball_detection_requested
        )
        
        if not sequence_result.get("success", False):
            raise RuntimeError("序列分析失败")
        
        print("✅ 姿态分析完成")
        
        ball_detections = sequence_result.get("ball_detections", []) if ball_detection_requested else []
        if highlight_ball and not sequence_result.get("ball_detection_enabled", False):
            print("⚠️ Volleyball detection unavailable, skipping ball overlay.")
            highlight_ball = False
        ball_overlay_data = ball_detections if highlight_ball else None
        
        # 生成处理后的帧
        print(f"🎨 开始生成{video_type} 视频...")
        
        if video_type == "overlay":
            processed_frames = self._generate_overlay_frames(frames, sequence_result, ball_overlay_data, highlight_ball)
            # processed_frames = sequence_result['annotated_frames']
        elif video_type == "skeleton":
            processed_frames = self._generate_skeleton_frames(sequence_result)
        elif video_type == "comparison":
            processed_frames = self._generate_comparison_frames(frames, sequence_result, ball_overlay_data, highlight_ball)
        elif video_type == "trajectory":
            processed_frames = self._generate_trajectory_frames(frames, sequence_result, ball_overlay_data, highlight_ball)
        else:
            raise ValueError(f"未知的视频类型 {video_type}")

        # 直接用FFmpeg或OpenCV写入浏览器兼容格式
        final_result = self._write_web_compatible_video(processed_frames, output_path, fps)
        
        print(f"🎉 视频生成完成: {final_result}")
        return final_result
    
    def _generate_overlay_frames(self, frames, sequence_result, ball_detections=None, highlight_ball=False):
        """生成骨架叠加帧"""
        processed_frames = []
        for idx, frame in enumerate(frames):
            frame_data = sequence_result['frames_data'][idx]
            landmarks = frame_data['landmarks']
            overlay_frame = frame.copy()
            frame_ball = self._get_ball_detections(ball_detections, idx) if highlight_ball else []
            
            if landmarks:
                overlay_frame = self._draw_skeleton(overlay_frame, landmarks)
                cv2.putText(overlay_frame, f"Frame {idx + 1}/{len(frames)}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(overlay_frame, f"Frame {idx + 1}/{len(frames)} - No Pose", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            if highlight_ball and frame_ball:
                overlay_frame = self._draw_ball_markers(overlay_frame, frame_ball)
            
            processed_frames.append(overlay_frame)
        return processed_frames
    
    def _generate_skeleton_frames(self, sequence_result, width=640, height=480):
        """生成纯骨架帧"""
        processed_frames = []
        frames_data = sequence_result['frames_data']
        
        for idx, frame_data in enumerate(frames_data):
            skeleton_frame = np.ones((height, width, 3), dtype=np.uint8) * 255
            landmarks = frame_data['landmarks']
            
            if landmarks:
                skeleton_frame = self._draw_skeleton(
                    skeleton_frame, landmarks,
                    point_color=(0, 0, 255), line_color=(0, 0, 0),
                    point_radius=8, line_thickness=3
                )
            
            processed_frames.append(skeleton_frame)
        return processed_frames
    
    def _generate_comparison_frames(self, frames, sequence_result, ball_detections=None, highlight_ball=False):
        """生成左右对比帧"""
        processed_frames = []
        height, width = frames[0].shape[:2]
        
        for idx, frame in enumerate(frames):
            # 左侧：原视频
            left = frame.copy()
            frame_ball = self._get_ball_detections(ball_detections, idx) if highlight_ball else []
            if highlight_ball and frame_ball:
                left = self._draw_ball_markers(left, frame_ball)
            
            # 右侧：纯骨架
            right = np.ones((height, width, 3), dtype=np.uint8) * 255
            frame_data = sequence_result['frames_data'][idx]
            landmarks = frame_data['landmarks']
            
            if landmarks:
                right = self._draw_skeleton(right, landmarks,
                    point_color=(0, 0, 255), line_color=(0, 0, 0),
                    point_radius=6, line_thickness=2)
            
            # 拼接
            comparison = np.hstack([left, right])
            processed_frames.append(comparison)
        return processed_frames
    
    def _generate_trajectory_frames(self, frames, sequence_result, ball_detections=None, highlight_ball=False):
        """生成轨迹追踪帧"""
        return self._generate_overlay_frames(frames, sequence_result, ball_detections, highlight_ball)  # 简化版
    
    # def _write_web_compatible_video(self, frames, output_path, fps):
    #     """写入浏览器兼容的视频"""
    #     import subprocess
    #     import tempfile
    #     import shutil
        
    #     if len(frames) == 0:
    #         raise ValueError("没有帧可以写入")
        
    #     height, width = frames[0].shape[:2]
        
    #     # 方法1: 使用FFmpeg（图片序列方式，更稳定）
    #     try:
    #         # 检查FFmpeg
    #         result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
    #         if result.returncode != 0:
    #             raise Exception("FFmpeg不可用")
            
    #         print("🔄 使用FFmpeg生成浏览器兼容视频...")
            
    #         # 创建临时目录保存帧
    #         temp_dir = tempfile.mkdtemp()
    #         print(f"📁 临时目录: {temp_dir}")
            
    #         try:
    #             # 保存所有帧为图片（高质量）
    #             print(f"💾 保存 {len(frames)} 帧为高质量图片...")
    #             for i, frame in enumerate(frames):
    #                 if frame is None:
    #                     print(f"⚠️ 第{i}帧为None，跳过")
    #                     continue
    #                 frame_path = os.path.join(temp_dir, f'frame_{i:06d}.png')
    #                 # 使用PNG压缩等级0（无压缩，最高质量）
    #                 success = cv2.imwrite(frame_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    #                 if not success:
    #                     print(f"⚠️ 第{i}帧保存失败")
                
    #             print("✅ 帧保存完成，开始FFmpeg合成...")
                
    #             # 尝试多种编码方案（高质量）
    #             codecs = [
    #                 ('h264_hq', ['-c:v', 'h264', '-pix_fmt', 'yuv420p', '-b:v', '5M']),  # H.264高码率
    #                 ('h264', ['-c:v', 'h264', '-pix_fmt', 'yuv420p']),  # H.264标准
    #                 ('mpeg4_hq', ['-c:v', 'mpeg4', '-q:v', '2', '-pix_fmt', 'yuv420p']),  # MPEG4高质量
    #                 ('mpeg4', ['-c:v', 'mpeg4', '-q:v', '5'])  # MPEG4标准
    #             ]
                
    #             result = None
    #             for codec_name, codec_args in codecs:
    #                 cmd = [
    #                     'ffmpeg', '-y',
    #                     '-framerate', str(fps),
    #                     '-i', os.path.join(temp_dir, 'frame_%06d.png')
    #                 ] + codec_args + [output_path]
                    
    #                 print(f"🎬 尝试编码器: {codec_name}")
    #                 result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
    #                 if result.returncode == 0 and os.path.exists(output_path):
    #                     print(f"✅ 使用 {codec_name} 编码成功")
    #                     break
    #                 else:
    #                     print(f"⚠️ {codec_name} 失败，尝试下一个...")
    #                     if os.path.exists(output_path):
    #                         os.remove(output_path)
                
    #             # 清理临时文件
    #             print("🗑️ 清理临时文件...")
    #             shutil.rmtree(temp_dir)
                
    #             if result.returncode == 0 and os.path.exists(output_path):
    #                 print("✅ FFmpeg生成成功（H.264编码）")
    #                 return output_path
    #             else:
    #                 stderr = result.stderr if result.stderr else "无错误输出"
    #                 print(f"⚠️ FFmpeg失败 (代码{result.returncode}): {stderr[:300]}")
                    
    #         except subprocess.TimeoutExpired:
    #             print("⚠️ FFmpeg执行超时")
    #             if os.path.exists(temp_dir):
    #                 shutil.rmtree(temp_dir)
    #             raise Exception("FFmpeg超时")
    #         except Exception as e:
    #             # 清理临时文件
    #             if os.path.exists(temp_dir):
    #                 shutil.rmtree(temp_dir)
    #             raise e
                
    #     except Exception as e:
    #         print(f"ℹ️ FFmpeg方案失败: {str(e)}")
        
    #     # 方法2: 使用OpenCV（降级方案）
    #     print("⚠️ 回退到OpenCV，视频可能无法在浏览器播放")
    #     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #     out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
    #     if not out.isOpened():
    #         raise RuntimeError("无法创建视频写入器")
        
    #     for frame in frames:
    #         out.write(frame)
        
    #     out.release()
        
    #     if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
    #         print("⚠️ 使用OpenCV生成，浏览器可能无法播放，请下载查看")
    #         return output_path
    #     else:
    #         raise RuntimeError("视频生成失败")
    
    def _write_web_compatible_video(self, frames, output_path, fps):
        """写入浏览器兼容的视频（优化版：使用 FFmpeg rawvideo 管道）"""
        import subprocess
        import os
        import cv2
        import numpy as np

        if len(frames) == 0:
            raise ValueError("没有帧可以写入")

        # 统一尺寸（假设所有帧尺寸已经一致，不一致就 resize）
        height, width = frames[0].shape[:2]

        # 先简单检查 ffmpeg 是否可用（可选）
        try:
            check = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if check.returncode != 0:
                raise RuntimeError("FFmpeg 不可用")
        except Exception as e:
            print(f"ℹ️ FFmpeg 检测失败，回退到 OpenCV: {e}")
            return self._write_video_opencv_fallback(frames, output_path, fps)

        print("🔄 使用 FFmpeg (rawvideo 管道) 生成浏览器兼容视频...")

        # FFmpeg 命令：从 stdin 读 raw BGR24 视频流
        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{width}x{height}',
            '-r', str(fps),
            '-i', '-',              # 从 stdin 读
            '-an',                  # 无音频
            '-vcodec', 'libx264',   # 或 'h264'，取决于你的 ffmpeg 构建
            '-pix_fmt', 'yuv420p',  # 浏览器最兼容的像素格式
            '-preset', 'fast',      # 编码预设：ultrafast, superfast, veryfast, faster, fast, medium(默认)
            '-crf', '23',           # 质量（18~28，越小越清晰）
            output_path
        ]

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            for i, frame in enumerate(frames):
                if frame is None:
                    continue

                # 如果有尺寸不一致的帧，这里统一 resize 一下
                if frame.shape[0] != height or frame.shape[1] != width:
                    frame = cv2.resize(frame, (width, height))

                # BGR np.ndarray → raw bytes
                proc.stdin.write(frame.tobytes())
        finally:
            proc.stdin.close()
            stderr = proc.stderr.read().decode('utf-8', errors='ignore')
            ret = proc.wait()

        if ret != 0 or not os.path.exists(output_path):
            print(f"⚠️ FFmpeg 生成失败，代码 {ret}，部分 stderr:\n{stderr[:300]}")
            print("⚠️ 回退到 OpenCV 方案...")
            return self._write_video_opencv_fallback(frames, output_path, fps)

        print("✅ FFmpeg 生成成功（H.264 + yuv420p，浏览器兼容）")
        return output_path


    def _write_video_opencv_fallback(self, frames, output_path, fps):
        """原来的 OpenCV 降级方案单独抽出来"""
        import os
        import cv2

        if len(frames) == 0:
            raise ValueError("没有帧可以写入")

        height, width = frames[0].shape[:2]
        print("⚠️ 回退到OpenCV，视频可能无法在浏览器播放")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        if not out.isOpened():
            raise RuntimeError("无法创建视频写入器")

        for frame in frames:
            if frame is None:
                continue
            out.write(frame)

        out.release()

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print("⚠️ 使用OpenCV生成，浏览器可能无法播放，请下载查看")
            return output_path
        else:
            raise RuntimeError("视频生成失败")

    
    def _convert_to_web_compatible(self, input_path, output_path):
        """
        将视频转换为浏览器兼容的H.264格式
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            
        Returns:
            str: 输出视频路径
        """
        try:
            # 尝试使用FFmpeg（如果可用）
            import subprocess
            
            # 检查FFmpeg是否可用
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                has_ffmpeg = True
            except:
                has_ffmpeg = False
            
            if has_ffmpeg:
                # 尝试多种FFmpeg命令（兼容不同版本）
                
                # 命令1: 完整参数（适用于完整版FFmpeg）
                cmd1 = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart',
                    output_path
                ]
                
                # 命令2: 基础参数（适用于精简版FFmpeg）
                cmd2 = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart',
                    output_path
                ]
                
                # 命令3: 最简参数（最大兼容性）
                cmd3 = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-vcodec', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    output_path
                ]
                
                # 依次尝试
                for i, cmd in enumerate([cmd1, cmd2, cmd3], 1):
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0 and os.path.exists(output_path):
                        print(f"✅ FFmpeg转换成功（方案{i}）")
                        # 删除临时文件
                        if os.path.exists(input_path):
                            os.remove(input_path)
                        return output_path
                    elif i == 3:  # 最后一次尝试失败
                        print(f"⚠️ FFmpeg所有方案都失败")
            
            # 如果FFmpeg不可用，使用OpenCV重新编码
            print("ℹ️ 使用OpenCV重新编码...")
            cap = cv2.VideoCapture(input_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 10
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 使用X264编码器
            fourcc = cv2.VideoWriter_fourcc(*'X264')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                # 如果X264不可用，尝试H264
                fourcc = cv2.VideoWriter_fourcc(*'H264')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if out.isOpened():
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out.write(frame)
                
                cap.release()
                out.release()
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    # 删除临时文件
                    if os.path.exists(input_path):
                        os.remove(input_path)
                    return output_path
            
            # 如果所有转换都失败，返回原始文件
            print("⚠️ 无法转换为H.264格式，使用原始视频")
            if not os.path.exists(output_path):
                os.rename(input_path, output_path)
            return output_path
            
        except Exception as e:
            print(f"⚠️ 转换过程出错: {str(e)}")
            # 如果转换失败，使用原始文件
            if not os.path.exists(output_path) and os.path.exists(input_path):
                os.rename(input_path, output_path)
            return output_path
    
    def create_overlay_video(self, frames, sequence_result, output_path=None, fps=10):
        """
        创建骨架叠加视频（方案1）
        
        Args:
            frames: 原始视频帧列表
            sequence_result: 序列分析结果（包含每帧的landmarks）
            output_path: 输出视频路径（如果为None则创建临时文件）
            fps: 输出视频帧率
            
        Returns:
            output_path: 生成的视频文件路径
        """
        if output_path is None:
            # 使用项目目录下的output文件夹
            output_dir = 'output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, f'volleyball_overlay_{id(sequence_result)}.mp4')
        
        # 获取视频参数
        height, width = frames[0].shape[:2]
        
        # 尝试多种编码格式，确保兼容性
        fourcc_list = [
            cv2.VideoWriter_fourcc(*'mp4v'),  # MPEG-4
            cv2.VideoWriter_fourcc(*'avc1'),  # H.264
            cv2.VideoWriter_fourcc(*'XVID'),  # Xvid
        ]
        
        out = None
        for fourcc in fourcc_list:
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            if out.isOpened():
                break
        
        if not out or not out.isOpened():
            raise RuntimeError("无法创建视频写入器，请检查OpenCV安装")
        
        # 处理每一帧
        for idx, frame in enumerate(frames):
            try:
                # 获取该帧的landmarks
                frame_data = sequence_result['frames_data'][idx]
                landmarks = frame_data['landmarks']
                
                # 复制帧，确保是正确的数据类型
                overlay_frame = frame.copy()
                
                # 确保帧是BGR格式，uint8类型
                if overlay_frame.dtype != np.uint8:
                    overlay_frame = overlay_frame.astype(np.uint8)
                
                if landmarks:
                    # 绘制骨架
                    overlay_frame = self._draw_skeleton(overlay_frame, landmarks)
                    
                    # 添加帧信息文字
                    cv2.putText(overlay_frame, f"Frame {idx + 1}/{len(frames)}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                else:
                    # 未检测到姿态
                    cv2.putText(overlay_frame, f"Frame {idx + 1}/{len(frames)} - No Pose Detected", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                # 写入帧（不检查返回值，因为OpenCV在Windows上返回值不可靠）
                out.write(overlay_frame)
                
            except Exception as e:
                # 如果单帧处理失败，记录但继续
                print(f"警告：处理第{idx+1}帧时出错: {str(e)}")
        
        # 释放资源
        out.release()
        
        # 验证文件是否生成
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError(f"视频文件生成失败: {output_path}")
        
        return output_path

    def _get_ball_detections(self, ball_detections, idx):
        if not ball_detections or idx is None:
            return []
        if idx >= len(ball_detections):
            return []
        return ball_detections[idx] or []

    def _draw_ball_markers(
        self,
        frame,
        detections,
        color=(0, 165, 255),
        marker="circle",
        trace=True,
        trace_len=8,
    ):
        """
        在帧上绘制排球标记（支持圆/方 + 轨迹）

        detections: [{ "bbox": (x1,y1,x2,y2), "label": str, "score": float }]
        """

        if frame is None:
            return frame

        h, w = frame.shape[:2]
        img = frame

        # -------------------------
        # 初始化轨迹队列
        # -------------------------
        if not hasattr(self, "_trace_queue"):
            from collections import deque
            self._trace_queue = deque([None] * trace_len, maxlen=trace_len)

        # -------------------------
        # 当前 bbox 进入队列
        # -------------------------
        if detections:
            det = detections[0]   # 目前只渲染一个球
            bbox = det.get("bbox")
            if bbox and len(bbox) == 4:
                x1, y1, x2, y2 = bbox

                # 边界裁剪
                x1 = max(0, min(w - 1, int(x1)))
                x2 = max(0, min(w - 1, int(x2)))
                y1 = max(0, min(h - 1, int(y1)))
                y2 = max(0, min(h - 1, int(y2)))

                cur_box = (x1, y1, x2, y2)
                self._trace_queue.appendleft(cur_box)
            else:
                self._trace_queue.appendleft(None)
        else:
            self._trace_queue.appendleft(None)

        # -------------------------
        # 开始绘制轨迹
        # -------------------------
        for i, box in enumerate(self._trace_queue):
            if box is None:
                continue

            x1, y1, x2, y2 = box

            # 当前帧 vs 历史轨迹
            is_current = (i == 0)

            if marker == "box":
                # 当前帧画粗线，历史帧画细线
                thickness = 2 if is_current else 1
                cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

            elif marker == "circle":
                # 计算圆心和半径
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                r = int(max((x2 - x1), (y2 - y1)) * 0.5)

                if is_current:
                    cv2.circle(img, (cx, cy), r, color, 5)
                else:
                    # cv2.circle(img, (cx, cy), max(r - 10, 2), color, -1)
                    cv2.circle(img, (cx, cy), 5, color, -1)
                    

        # -------------------------
        # 在当前帧写标签文字（可选）
        # -------------------------
        # if detections:
        #     det = detections[0]
        #     bbox = det.get("bbox", None)
        #     if bbox:
        #         x1, y1, x2, y2 = bbox
        #         label = det.get("label", "volleyball")
        #         score = det.get("score", 0.0)
        #         cv2.putText(
        #             img,
        #             f"{label}:{score:.2f}",
        #             (int(x1), max(0, int(y1) - 6)),
        #             cv2.FONT_HERSHEY_SIMPLEX,
        #             0.5,
        #             color,
        #             2,
        #         )

        return img

    
    def create_skeleton_video(self, sequence_result, output_path=None, fps=10, 
                             width=640, height=480, bg_color=(255, 255, 255)):
        """
        创建纯骨架动画视频（方案2）
        
        Args:
            sequence_result: 序列分析结果
            output_path: 输出视频路径
            fps: 输出视频帧率
            width: 视频宽度
            height: 视频高度
            bg_color: 背景颜色 (B, G, R)
            
        Returns:
            output_path: 生成的视频文件路径
        """
        if output_path is None:
            # 使用项目目录下的output文件夹
            output_dir = 'output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, f'volleyball_skeleton_{id(sequence_result)}.mp4')
        
        # 尝试多种编码格式
        fourcc_list = [
            cv2.VideoWriter_fourcc(*'mp4v'),
            cv2.VideoWriter_fourcc(*'avc1'),
            cv2.VideoWriter_fourcc(*'XVID'),
        ]
        
        out = None
        for fourcc in fourcc_list:
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            if out.isOpened():
                break
        
        if not out or not out.isOpened():
            raise RuntimeError("无法创建视频写入器")
        
        frames_data = sequence_result['frames_data']
        
        # 处理每一帧
        for idx, frame_data in enumerate(frames_data):
            try:
                # 创建白色背景
                skeleton_frame = np.ones((height, width, 3), dtype=np.uint8) * np.array(bg_color, dtype=np.uint8)
                
                landmarks = frame_data['landmarks']
                
                if landmarks:
                    # 绘制骨架（黑色，更清晰）
                    skeleton_frame = self._draw_skeleton(
                        skeleton_frame, 
                        landmarks,
                        point_color=(0, 0, 255),      # 红色关键点
                        line_color=(0, 0, 0),         # 黑色骨架线
                        point_radius=8,
                        line_thickness=3
                    )
                    
                    # 添加标题和帧信息
                    cv2.putText(skeleton_frame, "Skeleton Animation", 
                               (width//2 - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
                    cv2.putText(skeleton_frame, f"Frame {idx + 1}/{len(frames_data)}", 
                               (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
                else:
                    # 未检测到姿态
                    cv2.putText(skeleton_frame, "No Pose Detected", 
                               (width//2 - 100, height//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                    cv2.putText(skeleton_frame, f"Frame {idx + 1}/{len(frames_data)}", 
                               (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
                
                # 写入帧（不检查返回值）
                out.write(skeleton_frame)
                
            except Exception as e:
                print(f"警告：处理第{idx+1}帧时出错: {str(e)}")
        
        # 释放资源
        out.release()
        
        # 验证文件
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError(f"视频文件生成失败: {output_path}")
        
        return output_path
    
    def create_side_by_side_video(self, frames, sequence_result, output_path=None, fps=10):
        """
        创建左右对比视频：左侧原视频，右侧纯骨架
        
        Args:
            frames: 原始视频帧列表
            sequence_result: 序列分析结果
            output_path: 输出视频路径
            fps: 输出视频帧率
            
        Returns:
            output_path: 生成的视频文件路径
        """
        if output_path is None:
            # 使用项目目录下的output文件夹
            output_dir = 'output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, f'volleyball_comparison_{id(sequence_result)}.mp4')
        
        # 获取视频参数
        height, width = frames[0].shape[:2]
        
        # 尝试多种编码格式
        fourcc_list = [
            cv2.VideoWriter_fourcc(*'mp4v'),
            cv2.VideoWriter_fourcc(*'avc1'),
            cv2.VideoWriter_fourcc(*'XVID'),
        ]
        
        out = None
        for fourcc in fourcc_list:
            out = cv2.VideoWriter(output_path, fourcc, fps, (width * 2, height))
            if out.isOpened():
                break
        
        if not out or not out.isOpened():
            raise RuntimeError("无法创建视频写入器")
        
        frames_data = sequence_result['frames_data']
        
        # 处理每一帧
        for idx, frame in enumerate(frames):
            landmarks = frames_data[idx]['landmarks']
            
            # 左侧：原视频 + 骨架
            left_frame = frame.copy()
            if landmarks:
                left_frame = self._draw_skeleton(left_frame, landmarks)
            cv2.putText(left_frame, "Original + Skeleton", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 右侧：纯骨架
            right_frame = np.ones((height, width, 3), dtype=np.uint8) * 255
            if landmarks:
                right_frame = self._draw_skeleton(
                    right_frame, 
                    landmarks,
                    point_color=(0, 0, 255),
                    line_color=(0, 0, 0),
                    point_radius=8,
                    line_thickness=3
                )
            cv2.putText(right_frame, "Skeleton Only", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # 合并左右画面
            combined_frame = np.hstack([left_frame, right_frame])
            
            # 添加帧信息
            cv2.putText(combined_frame, f"Frame {idx + 1}/{len(frames)}", 
                       (width - 150, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 写入帧（不检查返回值）
            out.write(combined_frame)
        
        # 释放资源
        out.release()
        
        # 验证文件
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError(f"视频文件生成失败: {output_path}")
        
        return output_path
    
    def _draw_skeleton(self, frame, landmarks, point_color=(0, 255, 0), 
                      line_color=(0, 255, 0), point_radius=5, line_thickness=2):
        """
        在帧上绘制骨架
        
        Args:
            frame: 要绘制的帧
            landmarks: 关键点字典
            point_color: 关键点颜色
            line_color: 骨架线颜色
            point_radius: 关键点半径
            line_thickness: 骨架线粗细
            
        Returns:
            绘制后的帧
        """
        height, width = frame.shape[:2]
        
        # 创建关键点位置数组（用于连线）
        points = {}
        for name, idx in self.landmark_map.items():
            if name in landmarks:
                lm = landmarks[name]
                x = int(lm['x'] * width)
                y = int(lm['y'] * height)
                visibility = lm.get('visibility', 1.0)
                
                # 只绘制可见度高的点
                if visibility > 0.5:
                    points[idx] = (x, y)
        
        # 绘制连接线
        for connection in self.connections:
            start_idx, end_idx = connection
            if start_idx in points and end_idx in points:
                cv2.line(frame, points[start_idx], points[end_idx], 
                        line_color, line_thickness)
        
        # 绘制关键点
        for idx, point in points.items():
            cv2.circle(frame, point, point_radius, point_color, -1)
            # 添加点的标注（可选）
            # cv2.putText(frame, str(idx), point, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        return frame
    
    def create_trajectory_video(self, frames, sequence_result, output_path=None, fps=10):
        """
        创建轨迹追踪视频：显示关键点的运动轨迹
        
        Args:
            frames: 原始视频帧列表
            sequence_result: 序列分析结果
            output_path: 输出视频路径
            fps: 输出视频帧率
            
        Returns:
            output_path: 生成的视频文件路径
        """
        if output_path is None:
            # 使用项目目录下的output文件夹
            output_dir = 'output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, f'volleyball_trajectory_{id(sequence_result)}.mp4')
        
        # 获取视频参数
        height, width = frames[0].shape[:2]
        
        # 尝试多种编码格式
        fourcc_list = [
            cv2.VideoWriter_fourcc(*'mp4v'),
            cv2.VideoWriter_fourcc(*'avc1'),
            cv2.VideoWriter_fourcc(*'XVID'),
        ]
        
        out = None
        for fourcc in fourcc_list:
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            if out.isOpened():
                break
        
        if not out or not out.isOpened():
            raise RuntimeError("无法创建视频写入器")
        
        # 收集轨迹点
        trajectories = sequence_result['trajectories']
        
        # 处理每一帧
        for idx, frame in enumerate(frames):
            trajectory_frame = frame.copy()
            
            # 绘制当前帧之前的轨迹
            for point_name in ['left_wrist', 'right_wrist']:
                if point_name not in trajectories:
                    continue
                
                traj = trajectories[point_name]
                color = (255, 0, 0) if 'left' in point_name else (0, 0, 255)
                
                # 绘制轨迹线
                points_to_draw = []
                for i in range(min(idx + 1, len(traj['x']))):
                    x = traj['x'][i]
                    y = traj['y'][i]
                    vis = traj['visibility'][i]
                    
                    if x is not None and y is not None and vis > 0.5:
                        px = int(x * width)
                        py = int(y * height)
                        points_to_draw.append((px, py))
                
                # 绘制轨迹点和连线
                for i in range(1, len(points_to_draw)):
                    # 线条透明度渐变
                    alpha = 0.3 + 0.7 * (i / max(1, len(points_to_draw) - 1))
                    cv2.line(trajectory_frame, points_to_draw[i-1], points_to_draw[i], 
                            color, 2)
                
                # 当前点加粗显示
                if len(points_to_draw) > 0:
                    cv2.circle(trajectory_frame, points_to_draw[-1], 8, color, -1)
            
            # 绘制当前骨架
            landmarks = sequence_result['frames_data'][idx]['landmarks']
            if landmarks:
                trajectory_frame = self._draw_skeleton(trajectory_frame, landmarks, 
                                                      point_color=(0, 255, 0),
                                                      line_color=(0, 255, 0),
                                                      point_radius=5,
                                                      line_thickness=2)
            
            # 添加标题和说明
            cv2.putText(trajectory_frame, "Motion Trajectory", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(trajectory_frame, f"Frame {idx + 1}/{len(frames)}", 
                       (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # 图例
            cv2.rectangle(trajectory_frame, (width - 150, 10), (width - 10, 80), (0, 0, 0), -1)
            cv2.putText(trajectory_frame, "Left Wrist", (width - 140, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            cv2.putText(trajectory_frame, "Right Wrist", (width - 140, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # 写入帧（不检查返回值）
            out.write(trajectory_frame)
        
        # 释放资源
        out.release()
        
        # 验证文件
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError(f"视频文件生成失败: {output_path}")
        
        return output_path

