"""
评分算法模块 V3 - 智能评分版
新增功能：
1. 高斯/sigmoid非线性评分 - 替代简单线性比较
2. 人球位置评分 - 结合球体检测
3. 动态权重系统 - 根据检测置信度调整
4. 上下文感知 - 考虑动作阶段
"""
import numpy as np
import json
from .pose_detector import PoseDetector


class VolleyballScorerV3:
    def __init__(self, template_path='template.json'):
        """初始化智能评分器"""
        self.template = self._load_template(template_path)
        self.detector = PoseDetector()
        
        # 优化后的标准值（基于专业垫球动作）
        self.standards = {
            "arm_angle_range": (140, 175),      # 手臂角度：略微弯曲更利于控球
            "arm_gap_range": (20, 40),          # 双臂间距：收紧标准
            "knee_angle_range": (80, 110),      # 膝盖角度：标准半蹲姿势
            "wrist_hip_ratio_range": (0.8, 1.5),
            "torso_angle_range": (75, 105),
            # 新增：人球位置标准
            "ball_vertical_offset_range": (0.05, 0.18),  # 球在手腕上方5-18cm（更实战）
            "ball_horizontal_offset_max": 0.12,  # 球在身体中线左右12cm内
            "ball_contact_distance_max": 0.12,   # 接触距离
        }
    
    def _load_template(self, path):
        """加载标准动作模板"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    # ==================== 智能评分函数 ====================
    
    def _gaussian_score(self, value, ideal, tolerance, max_score):
        """
        高斯评分曲线 - 在理想值附近得分最高（优化版：更温和）
        
        Args:
            value: 实际值
            ideal: 理想值
            tolerance: 容忍度（标准差）
            max_score: 最高分数
            
        Returns:
            得分
        """
        deviation = abs(value - ideal) / tolerance
        # 降低衰减系数从0.5到0.3，让衰减更温和
        return max_score * np.exp(-0.3 * deviation**2)
    
    def _sigmoid_score(self, value, threshold, steepness=5, max_score=100):
        """
        Sigmoid评分 - 用于阈值类评分
        
        Args:
            value: 实际值
            threshold: 阈值
            steepness: 陡峭度（越大曲线越陡）
            max_score: 最高分数
            
        Returns:
            得分
        """
        normalized = 1 / (1 + np.exp(-steepness * (value - threshold)))
        return normalized * max_score
    
    def _range_gaussian_score(self, value, min_val, max_val, max_score):
        """
        范围高斯评分 - 在范围内满分，范围外高斯衰减（优化版：更温和）
        
        Args:
            value: 实际值
            min_val: 最小理想值
            max_val: 最大理想值
            max_score: 最高分数
        """
        if min_val <= value <= max_val:
            return max_score
        
        # 计算偏离理想范围的程度
        ideal_center = (min_val + max_val) / 2
        tolerance = (max_val - min_val) / 2
        
        if value < min_val:
            deviation = (min_val - value) / tolerance
        else:
            deviation = (value - max_val) / tolerance
        
        # 高斯衰减（降低衰减系数从0.5到0.25，让衰减更温和）
        # 现在偏差=tolerance时，分数为78%而非61%
        return max(0, max_score * np.exp(-0.25 * deviation**2))
    
    # ==================== 身高计算 ====================
    
    def calculate_body_height(self, landmarks):
        """计算人体身高（归一化）"""
        try:
            nose_y = landmarks['nose']['y']
            ankle_y = (landmarks['left_ankle']['y'] + landmarks['right_ankle']['y']) / 2
            height_1 = abs(ankle_y - nose_y)
            
            shoulder_y = (landmarks['left_shoulder']['y'] + landmarks['right_shoulder']['y']) / 2
            height_2 = abs(ankle_y - shoulder_y) * 1.15
            
            estimated_height = (height_1 + height_2) / 2
            return estimated_height
        except Exception as e:
            return 1.0
    
    def get_adaptive_standards(self, body_height):
        """根据身高调整标准值（优化版）"""
        height_factor = body_height / 0.7
        adjusted = self.standards.copy()
        
        # 高个子：允许膝盖角度稍大，手臂角度稍小
        if height_factor > 1.1:
            adjusted["arm_angle_range"] = (135, 170)
            adjusted["knee_angle_range"] = (85, 115)
        # 矮个子：允许膝盖角度稍小，保持手臂标准
        elif height_factor < 0.9:
            adjusted["arm_angle_range"] = (140, 175)
            adjusted["knee_angle_range"] = (75, 105)
        
        return adjusted
    
    # ==================== 人球位置评分（新增）====================
    
    def _score_ball_contact(self, landmarks, ball_detection, body_height):
        """
        评估人球位置关系（新增核心功能）
        
        Args:
            landmarks: 人体关键点
            ball_detection: VolleyballDetection对象（包含 label, score, bbox, center）
            body_height: 归一化身高
            
        Returns:
            tuple: (得分, 反馈列表)
        """
        feedback = []
        
        if ball_detection is None:
            return 0, ['⚪ 未检测到排球（评分仅基于人体姿态）']
        
        try:
            # 1. 获取球的中心位置（归一化坐标）
            ball_x, ball_y = ball_detection.center
            
            # 2. 获取手腕位置
            wrist_x = (landmarks['left_wrist']['x'] + landmarks['right_wrist']['x']) / 2
            wrist_y = (landmarks['left_wrist']['y'] + landmarks['right_wrist']['y']) / 2
            
            # 3. 获取身体中心线
            body_center_x = (landmarks['left_shoulder']['x'] + landmarks['right_shoulder']['x']) / 2
            
            # 4. 计算相对位置
            vertical_offset = wrist_y - ball_y  # 正值=球在手腕上方（因为y向下增大）
            horizontal_offset = abs(ball_x - body_center_x)
            ball_wrist_distance = np.sqrt((ball_x - wrist_x)**2 + (ball_y - wrist_y)**2)
            
            # 5. 垂直位置评分（满分10分）- 使用高斯评分
            ideal_vertical = 0.15  # 理想：球在手腕上方15%
            tolerance = 0.12       # 增加容忍度（更实战）
            vertical_score = self._gaussian_score(
                -vertical_offset,  # 转换为正数（球在上方）
                ideal_vertical,
                tolerance,
                max_score=10
            )
            
            if -0.18 <= vertical_offset <= -0.05:  # 球在手腕上方5-18cm
                feedback.append('✅ 球的高度理想')
            elif vertical_offset > 0:  # 球低于手腕
                feedback.append('⚠️ 球的位置偏低，应在手腕上方')
                vertical_score *= 0.5
            else:  # 球过高
                feedback.append('⚠️ 球的位置偏高，注意提前准备')
                vertical_score *= 0.7
            
            # 6. 水平对齐评分（满分8分）- 使用高斯评分
            horizontal_score = self._gaussian_score(
                horizontal_offset,
                ideal=0,  # 理想：球在身体中线
                tolerance=0.12,  # 增加容忍度（允许适度偏离）
                max_score=8
            )
            
            if horizontal_offset < 0.08:
                feedback.append('✅ 球在身体正前方')
            elif horizontal_offset < 0.12:
                feedback.append('⚠️ 球略微偏离中线，可调整站位')
            elif horizontal_offset < 0.18:
                feedback.append('⚠️ 调整站位，让球更靠近身体中线')
            else:
                feedback.append('❌ 站位偏离过大，快速移动到位')
            
            # 7. 接触距离评分（满分7分）- 使用sigmoid评分
            # 距离越近越好，但要避免过近（小于0.02）
            if ball_wrist_distance < 0.02:
                # 太近了，可能已经过了接触点
                distance_score = 3.5
                feedback.append('⚠️ 球已经接近或通过手腕，注意提前准备')
            else:
                # 使用反sigmoid：距离越小分数越高（降低陡峭度）
                distance_score = self._sigmoid_score(
                    -ball_wrist_distance,  # 负值，距离小时值大
                    threshold=-0.10,       # 调整阈值
                    steepness=20,          # 降低陡峭度（更温和）
                    max_score=7
                )
                
                if ball_wrist_distance < 0.10:
                    feedback.append('✅ 接触时机准确')
                elif ball_wrist_distance < 0.18:
                    feedback.append('⚠️ 球距离略远，建议移动到位')
                else:
                    feedback.append('❌ 球距离较远，快速移动到位')
            
            # 8. 球的检测置信度加权（优化：降低惩罚）
            # 使用平方根减轻低置信度的过度惩罚
            confidence_factor = np.sqrt(min(1.0, ball_detection.score))
            
            total_ball_score = (vertical_score + horizontal_score + distance_score) * confidence_factor
            
            # 添加置信度反馈
            if ball_detection.score < 0.4:
                feedback.append('⚠️ 球体检测置信度较低，可能影响评分准确性')
            elif ball_detection.score < 0.6:
                feedback.append('ℹ️ 球体检测置信度一般')
            
            return min(25, total_ball_score), feedback
            
        except Exception as e:
            return 0, [f'❌ 人球位置分析异常: {str(e)}']
    
    # ==================== 动态权重评分（新增）====================
    
    def score_pose_with_ball(self, landmarks, ball_detection=None):
        """
        带球体检测的智能评分（核心函数）
        
        Args:
            landmarks: 人体关键点
            ball_detection: 球体检测结果（可选）
            
        Returns:
            dict: 评分结果
        """
        if landmarks is None:
            return {
                'total_score': 0,
                'arm_score': 0,
                'body_score': 0,
                'position_score': 0,
                'ball_score': 0,
                'stability_score': 0,
                'has_ball': False,
                'feedback': ['未检测到人体姿态，请确保全身入镜']
            }
        
        # 计算身高并获取自适应标准
        body_height = self.calculate_body_height(landmarks)
        standards = self.get_adaptive_standards(body_height)
        
        scores = {}
        feedback = []
        
        # 检测是否有球
        has_ball = ball_detection is not None and ball_detection.score > 0.5
        
        # ========== 动态权重系统（优化版）==========
        if has_ball:
            # 有球时：强调身体重心（腿功重于手功）
            # 总分 = 手臂(28) + 身体(30) + 姿态位置(12) + 人球位置(25) + 稳定性(5)
            weights = {
                'arm': 28,
                'body': 30,      # 提高身体权重
                'position': 12,  # 适度提高触球位置权重
                'ball': 25,      # 降低人球位置权重
                'stability': 5
            }
            feedback.append('🏐 【智能评分模式：已检测到排球】')
        else:
            # 无球时：同样强调身体重心
            # 总分 = 手臂(32) + 身体(33) + 姿态位置(25) + 稳定性(10)
            weights = {
                'arm': 32,
                'body': 33,      # 提高身体权重
                'position': 25,
                'ball': 0,
                'stability': 10
            }
            feedback.append('📋 【标准评分模式：基于人体姿态】')
        
        # 1. 手臂评分 - 使用高斯评分
        arm_score, arm_feedback = self._score_arms_v3(landmarks, standards, weights['arm'])
        scores['arm_score'] = arm_score
        feedback.extend(arm_feedback)
        
        # 2. 身体重心评分 - 使用高斯评分
        body_score, body_feedback = self._score_body_v3(landmarks, standards, weights['body'])
        scores['body_score'] = body_score
        feedback.extend(body_feedback)
        
        # 3. 触球位置评分 - 使用高斯评分
        position_score, position_feedback = self._score_position_v3(
            landmarks, standards, body_height, weights['position']
        )
        scores['position_score'] = position_score
        feedback.extend(position_feedback)
        
        # 4. 人球位置评分（新增）
        if has_ball:
            ball_score, ball_feedback = self._score_ball_contact(
                landmarks, ball_detection, body_height
            )
            scores['ball_score'] = ball_score
            feedback.extend(ball_feedback)
        else:
            scores['ball_score'] = 0
        
        # 5. 稳定性评分
        stability_score, stability_feedback = self._score_stability(landmarks, weights['stability'])
        scores['stability_score'] = stability_score
        feedback.extend(stability_feedback)
        
        # 计算总分（确保转换为Python原生类型）
        total_score = int(
            arm_score + body_score + position_score + 
            scores['ball_score'] + stability_score
        )
        scores['total_score'] = int(min(100, total_score))  # 限制最高100分
        scores['arm_score'] = float(arm_score)
        scores['body_score'] = float(body_score)
        scores['position_score'] = float(position_score)
        scores['ball_score'] = float(scores['ball_score'])
        scores['stability_score'] = float(stability_score)
        scores['feedback'] = feedback
        scores['has_ball'] = bool(has_ball)
        
        # 添加每个部分的满分信息
        scores['max_scores'] = {
            'arm_max': int(weights['arm']),
            'body_max': int(weights['body']),
            'position_max': int(weights['position']),
            'ball_max': int(weights['ball']),
            'stability_max': int(weights['stability']),
            'total_max': 100
        }
        
        return scores
    
    # ==================== 改进的分项评分（使用高斯/sigmoid）====================
    
    def _score_arms_v3(self, landmarks, standards, max_score):
        """手臂评分 - 使用高斯评分"""
        feedback = []
        
        try:
            # 计算角度
            left_angle = self.detector.calculate_angle(
                landmarks['left_shoulder'],
                landmarks['left_elbow'],
                landmarks['left_wrist']
            )
            
            right_angle = self.detector.calculate_angle(
                landmarks['right_shoulder'],
                landmarks['right_elbow'],
                landmarks['right_wrist']
            )
            
            shoulder_center = {
                'x': (landmarks['left_shoulder']['x'] + landmarks['right_shoulder']['x']) / 2,
                'y': (landmarks['left_shoulder']['y'] + landmarks['right_shoulder']['y']) / 2
            }
            arm_gap = self.detector.calculate_angle(
                landmarks['left_wrist'],
                shoulder_center,
                landmarks['right_wrist']
            )
            
            # 使用高斯评分
            arm_min, arm_max = standards["arm_angle_range"]
            gap_min, gap_max = standards["arm_gap_range"]
            
            left_score = self._range_gaussian_score(
                left_angle, arm_min, arm_max, max_score * 0.4
            )
            right_score = self._range_gaussian_score(
                right_angle, arm_min, arm_max, max_score * 0.4
            )
            gap_score = self._range_gaussian_score(
                arm_gap, gap_min, gap_max, max_score * 0.2
            )
            
            total_arm_score = left_score + right_score + gap_score
            
            # 生成反馈（与评分标准一致：140-175°）
            if left_angle < 130:
                feedback.append('⚠️ 左臂弯曲过多，影响击球稳定性')
            elif left_angle < 140:
                feedback.append('⚠️ 左臂可以稍微伸直一些')
            elif 140 <= left_angle <= 175:
                feedback.append('✅ 左臂姿势标准')
            else:  # > 175
                feedback.append('⚠️ 左臂过于伸直，建议略微弯曲保持弹性')
            
            if right_angle < 130:
                feedback.append('⚠️ 右臂弯曲过多，影响击球稳定性')
            elif right_angle < 140:
                feedback.append('⚠️ 右臂可以稍微伸直一些')
            elif 140 <= right_angle <= 175:
                feedback.append('✅ 右臂姿势标准')
            else:  # > 175
                feedback.append('⚠️ 右臂过于伸直，建议略微弯曲保持弹性')
            
            if 20 <= arm_gap <= 40:
                feedback.append('✅ 双臂间距标准')
            elif arm_gap < 20:
                feedback.append('⚠️ 双臂可以稍微打开一些（保持20-40°）')
            elif arm_gap > 45:
                feedback.append('⚠️ 双臂距离过宽，收紧至肩宽')
            
            return total_arm_score, feedback
            
        except Exception as e:
            return 0, [f'手臂姿态识别异常: {str(e)}']
    
    def _score_body_v3(self, landmarks, standards, max_score):
        """身体评分 - 使用高斯评分"""
        feedback = []
        
        try:
            left_knee_angle = self.detector.calculate_angle(
                landmarks['left_hip'],
                landmarks['left_knee'],
                landmarks['left_ankle']
            )
            
            right_knee_angle = self.detector.calculate_angle(
                landmarks['right_hip'],
                landmarks['right_knee'],
                landmarks['right_ankle']
            )
            
            knee_min, knee_max = standards["knee_angle_range"]
            
            left_knee_score = self._range_gaussian_score(
                left_knee_angle, knee_min, knee_max, max_score * 0.4
            )
            right_knee_score = self._range_gaussian_score(
                right_knee_angle, knee_min, knee_max, max_score * 0.4
            )
            
            # 平衡性评分 - 使用高斯评分
            knee_diff = abs(left_knee_angle - right_knee_angle)
            balance_score = self._gaussian_score(
                knee_diff, ideal=0, tolerance=15, max_score=max_score * 0.2
            )
            
            total_body_score = left_knee_score + right_knee_score + balance_score
            
            # 生成反馈（与评分标准一致：80-110°）
            if 80 <= left_knee_angle <= 110:
                feedback.append('✅ 左腿弯曲标准（重心稳定）')
            elif left_knee_angle > 120:
                feedback.append('⚠️ 左腿弯曲不足，请降低重心至半蹲')
            elif left_knee_angle < 70:
                feedback.append('⚠️ 左腿蹲得过低，重心过低影响移动')
            else:
                feedback.append('⚠️ 左腿弯曲略有偏差')
            
            if 80 <= right_knee_angle <= 110:
                feedback.append('✅ 右腿弯曲标准（重心稳定）')
            elif right_knee_angle > 120:
                feedback.append('⚠️ 右腿弯曲不足，请降低重心至半蹲')
            elif right_knee_angle < 70:
                feedback.append('⚠️ 右腿蹲得过低，重心过低影响移动')
            else:
                feedback.append('⚠️ 右腿弯曲略有偏差')
            
            if knee_diff < 15:
                feedback.append('✅ 双腿平衡稳定')
            else:
                feedback.append('⚠️ 注意双腿平衡')
            
            return total_body_score, feedback
            
        except Exception as e:
            return 0, [f'身体重心识别异常: {str(e)}']
    
    def _score_position_v3(self, landmarks, standards, body_height, max_score):
        """位置评分 - 使用高斯评分"""
        feedback = []
        
        try:
            wrist_y = (landmarks['left_wrist']['y'] + landmarks['right_wrist']['y']) / 2
            shoulder_y = (landmarks['left_shoulder']['y'] + landmarks['right_shoulder']['y']) / 2
            hip_y = (landmarks['left_hip']['y'] + landmarks['right_hip']['y']) / 2
            knee_y = (landmarks['left_knee']['y'] + landmarks['right_knee']['y']) / 2
            
            # 计算手腕相对位置
            shoulder_knee_range = abs(knee_y - shoulder_y)
            if shoulder_knee_range > 0:
                wrist_position = (wrist_y - shoulder_y) / shoulder_knee_range
            else:
                wrist_position = 0
            
            # 使用高斯评分 - 理想位置：0.8（肩膝之间偏下）
            position_score = self._gaussian_score(
                wrist_position,
                ideal=0.8,
                tolerance=0.3,
                max_score=max_score
            )
            
            # 生成反馈
            if hip_y <= wrist_y <= knee_y:
                feedback.append('✅ 触球位置标准（腰腹前下方）')
            elif wrist_y < shoulder_y:
                feedback.append('❌ 触球位置过高')
                position_score *= 0.5
            elif wrist_y > knee_y:
                feedback.append('❌ 触球位置过低')
                position_score *= 0.7
            else:
                feedback.append('⚠️ 触球位置略有偏差')
            
            return position_score, feedback
            
        except Exception as e:
            return 0, [f'触球位置识别异常: {str(e)}']
    
    def _score_stability(self, landmarks, max_score):
        """稳定性评分"""
        feedback = []
        
        try:
            key_points = ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                         'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
                         'left_knee', 'right_knee']
            
            visibilities = [landmarks[point]['visibility'] for point in key_points]
            avg_visibility = float(np.mean(visibilities))  # 转换为Python float
            
            # 使用sigmoid评分
            stability_score = float(self._sigmoid_score(
                avg_visibility,
                threshold=0.5,
                steepness=10,
                max_score=max_score
            ))
            
            if avg_visibility > 0.75:
                feedback.append('✅ 姿态识别清晰')
            elif avg_visibility > 0.5:
                feedback.append('⚠️ 姿态识别一般')
            else:
                feedback.append('❌ 姿态识别不清晰')
            
            return stability_score, feedback
            
        except Exception as e:
            return 0.0, [f'稳定性评估异常: {str(e)}']
    
    # ==================== 序列评分 ====================
    
    def score_sequence_with_ball(self, frames_data):
        """
        带球体检测的序列评分
        
        Args:
            frames_data: 帧数据列表，每个元素包含 {'landmarks': ..., 'ball': ...}
            
        Returns:
            dict: 序列评分结果
        """
        if not frames_data or len(frames_data) == 0:
            return {
                'total_score': 0,
                'best_frame_score': 0,
                'has_ball_frames': 0,
                'feedback': ['未检测到有效的动作序列']
            }
        
        # 评估每一帧
        frame_scores = []
        has_ball_count = 0
        
        for frame_data in frames_data:
            landmarks = frame_data.get('landmarks')
            ball = frame_data.get('ball')
            
            if landmarks is not None:
                score_result = self.score_pose_with_ball(landmarks, ball)
                frame_scores.append(score_result['total_score'])
                
                if score_result.get('has_ball', False):
                    has_ball_count += 1
            else:
                frame_scores.append(0)
        
        # 找到最佳帧
        best_frame_idx = int(np.argmax(frame_scores))  # 转换为Python int
        best_frame_score = int(frame_scores[best_frame_idx])  # 转换为Python int
        
        # 获取最佳帧的详细评分
        best_frame_data = frames_data[best_frame_idx]
        best_result = self.score_pose_with_ball(
            best_frame_data.get('landmarks'),
            best_frame_data.get('ball')
        )
        
        return {
            'total_score': int(best_frame_score),
            'best_frame_score': int(best_frame_score),
            'best_frame_idx': int(best_frame_idx),
            'has_ball_frames': int(has_ball_count),
            'ball_detection_rate': float(has_ball_count / len(frames_data)) if frames_data else 0.0,
            'arm_score': float(best_result.get('arm_score', 0)),
            'body_score': float(best_result.get('body_score', 0)),
            'position_score': float(best_result.get('position_score', 0)),
            'ball_score': float(best_result.get('ball_score', 0)),
            'stability_score': float(best_result.get('stability_score', 0)),
            'feedback': best_result.get('feedback', [])
        }
    
    def get_grade(self, score):
        """根据分数返回等级"""
        if score >= 85:
            return 'S', '完美！职业级水准！🏆'
        elif score >= 75:
            return 'A', '优秀！继续保持！⭐'
        elif score >= 65:
            return 'B', '良好！再接再厉！👍'
        elif score >= 55:
            return 'C', '及格！继续努力！💪'
        else:
            return 'D', '需要改进！多多练习！📚'




