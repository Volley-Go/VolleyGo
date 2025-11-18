"""
评分算法模块 V2 - 优化版
解决问题：
1. 及格率低 - 调整评分曲线和标准值
2. 击球位置判断不准 - 改进相对位置计算
3. 只看单帧 - 引入序列分析
4. 没有身高自适应 - 添加自适应标准
"""
import numpy as np
import json
from .pose_detector import PoseDetector


class VolleyballScorerV2:
    def __init__(self, template_path='template.json'):
        """初始化评分器"""
        self.template = self._load_template(template_path)
        self.detector = PoseDetector()
        
        # 优化后的标准值（更宽松、更科学）
        self.standards = {
            # 手臂标准（范围而非固定值）
            "arm_angle_range": (150, 180),      # 手臂伸直角度范围
            "arm_gap_range": (15, 45),          # 双臂夹角范围
            
            # 膝盖标准（更宽容）
            "knee_angle_range": (60, 120),      # 膝盖弯曲范围
            
            # 触球高度（相对身高）
            "wrist_hip_ratio_range": (0.8, 1.5),  # 手腕相对髋部的高度比
            
            # 身体前倾角度
            "torso_angle_range": (75, 105),     # 躯干角度（垂直为90°）
        }
    
    def _load_template(self, path):
        """加载标准动作模板"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def calculate_body_height(self, landmarks):
        """
        计算人体身高（用于自适应标准）
        基于多个关键点的平均距离
        """
        try:
            # 方法1：头到脚踝的距离
            nose_y = landmarks['nose']['y']
            ankle_y = (landmarks['left_ankle']['y'] + landmarks['right_ankle']['y']) / 2
            height_1 = abs(ankle_y - nose_y)
            
            # 方法2：肩到脚踝 + 估算头部
            shoulder_y = (landmarks['left_shoulder']['y'] + landmarks['right_shoulder']['y']) / 2
            height_2 = abs(ankle_y - shoulder_y) * 1.15  # 头部约占15%
            
            # 取平均值
            estimated_height = (height_1 + height_2) / 2
            
            return estimated_height
            
        except Exception as e:
            return 1.0  # 默认归一化高度
    
    def get_adaptive_standards(self, body_height):
        """
        根据身高调整标准值
        
        Args:
            body_height: 归一化身高（0-1）
        
        Returns:
            adjusted_standards: 调整后的标准值字典
        """
        # 身高系数（身高越高，某些角度标准会略有调整）
        height_factor = body_height / 0.7  # 假设0.7是平均归一化高度
        
        adjusted = self.standards.copy()
        
        # 根据身高微调标准
        # 高个子：手臂角度可以略小，因为重心更高
        if height_factor > 1.1:
            adjusted["arm_angle_range"] = (145, 180)
            adjusted["knee_angle_range"] = (65, 125)
        # 矮个子：膝盖可以弯得更多，重心更低
        elif height_factor < 0.9:
            adjusted["arm_angle_range"] = (150, 180)
            adjusted["knee_angle_range"] = (55, 115)
        
        return adjusted
    
    def score_pose(self, landmarks):
        """
        对姿态进行评分（优化版）
        
        Args:
            landmarks: 姿态关键点字典
            
        Returns:
            dict: 包含总分和各项得分的字典
        """
        if landmarks is None:
            return {
                'total_score': 0,
                'arm_score': 0,
                'body_score': 0,
                'position_score': 0,
                'stability_score': 0,
                'feedback': ['未检测到人体姿态，请确保全身入镜']
            }
        
        # 计算身高并获取自适应标准
        body_height = self.calculate_body_height(landmarks)
        standards = self.get_adaptive_standards(body_height)
        
        scores = {}
        feedback = []
        
        # 1. 手臂评分 (35分) - 降低权重
        arm_score, arm_feedback = self._score_arms_v2(landmarks, standards)
        scores['arm_score'] = arm_score
        feedback.extend(arm_feedback)
        
        # 2. 身体重心评分 (30分)
        body_score, body_feedback = self._score_body_v2(landmarks, standards)
        scores['body_score'] = body_score
        feedback.extend(body_feedback)
        
        # 3. 触球位置评分 (25分) - 提高权重，改进算法
        position_score, position_feedback = self._score_position_v2(landmarks, standards, body_height)
        scores['position_score'] = position_score
        feedback.extend(position_feedback)
        
        # 4. 整体稳定性评分 (10分)
        stability_score, stability_feedback = self._score_stability(landmarks)
        scores['stability_score'] = stability_score
        feedback.extend(stability_feedback)
        
        # 计算总分
        scores['total_score'] = int(arm_score + body_score + position_score + stability_score)
        scores['feedback'] = feedback
        
        return scores
    
    def score_sequence(self, landmarks_sequence):
        """
        对动作序列进行评分（新增）
        
        Args:
            landmarks_sequence: 关键点序列列表 [frame1_landmarks, frame2_landmarks, ...]
            
        Returns:
            dict: 包含序列评分和单帧评分的字典
        """
        if not landmarks_sequence or len(landmarks_sequence) == 0:
            return {
                'total_score': 0,
                'sequence_score': 0,
                'best_frame_score': 0,
                'smoothness': 0,
                'completeness': 0,
                'feedback': ['未检测到有效的动作序列']
            }
        
        # 1. 评估每一帧
        frame_scores = []
        for landmarks in landmarks_sequence:
            if landmarks is not None:
                score_result = self.score_pose(landmarks)
                frame_scores.append(score_result['total_score'])
            else:
                frame_scores.append(0)
        
        # 2. 找到最佳帧
        best_frame_idx = int(np.argmax(frame_scores))  # 转换为Python int
        best_frame_score = int(frame_scores[best_frame_idx])  # 转换为Python int
        
        # 3. 评估流畅度（相邻帧的变化率）
        smoothness_score = self._calculate_smoothness(landmarks_sequence)
        
        # 4. 评估完整性（是否包含垫球的关键阶段）
        completeness_score = self._calculate_completeness(landmarks_sequence)
        
        # 5. 综合评分
        # 最佳帧占60%，流畅度占25%，完整性占15%
        # 注意：smoothness和completeness是0-1的比例，需要转换为满分100
        total_score = int(
            best_frame_score * 0.6 + 
            (smoothness_score * 100) * 0.25 + 
            (completeness_score * 100) * 0.15
        )
        
        # 6. 获取最佳帧的详细反馈
        best_landmarks = landmarks_sequence[best_frame_idx]
        if best_landmarks:
            best_frame_result = self.score_pose(best_landmarks)
            detailed_feedback = best_frame_result.get('feedback', [])
        else:
            detailed_feedback = []
        
        # 7. 生成综合反馈（包含详细反馈 + 序列反馈）
        feedback = []
        
        # 先添加动作质量反馈
        feedback.append('【最佳帧动作分析】')
        feedback.extend(detailed_feedback)
        
        # 再添加序列反馈
        feedback.append('')  # 空行分隔
        feedback.append('【动作连贯性分析】')
        if smoothness_score > 0.8:
            feedback.append('✅ 动作流畅自然')
        elif smoothness_score > 0.6:
            feedback.append('⚠️ 动作稍有停顿，可以更连贯')
        else:
            feedback.append('❌ 动作不够流畅，需要加强练习')
        
        if completeness_score > 0.8:
            feedback.append('✅ 动作完整规范')
        else:
            feedback.append('⚠️ 动作某些阶段不够完整')
        
        return {
            'total_score': int(total_score),
            'sequence_score': int(smoothness_score * 25 + completeness_score * 15),
            'best_frame_score': int(best_frame_score),
            'best_frame_idx': int(best_frame_idx),
            'smoothness': float(smoothness_score),
            'completeness': float(completeness_score),
            'frame_scores': [int(s) for s in frame_scores],  # 转换列表中的所有分数
            'feedback': feedback
        }
    
    def _score_arms_v2(self, landmarks, standards):
        """评分手臂姿态（优化版）"""
        feedback = []
        
        try:
            # 左臂角度
            left_angle = self.detector.calculate_angle(
                landmarks['left_shoulder'],
                landmarks['left_elbow'],
                landmarks['left_wrist']
            )
            
            # 右臂角度
            right_angle = self.detector.calculate_angle(
                landmarks['right_shoulder'],
                landmarks['right_elbow'],
                landmarks['right_wrist']
            )
            
            # 双臂夹角
            shoulder_center = {
                'x': (landmarks['left_shoulder']['x'] + landmarks['right_shoulder']['x']) / 2,
                'y': (landmarks['left_shoulder']['y'] + landmarks['right_shoulder']['y']) / 2
            }
            arm_gap = self.detector.calculate_angle(
                landmarks['left_wrist'],
                shoulder_center,
                landmarks['right_wrist']
            )
            
            # 计算得分（使用柔性评分曲线）
            arm_min, arm_max = standards["arm_angle_range"]
            gap_min, gap_max = standards["arm_gap_range"]
            
            # 左臂得分（满分12分）
            left_score = self._soft_range_score(left_angle, arm_min, arm_max, max_score=12)
            
            # 右臂得分（满分12分）
            right_score = self._soft_range_score(right_angle, arm_min, arm_max, max_score=12)
            
            # 双臂夹角得分（满分11分）
            gap_score = self._soft_range_score(arm_gap, gap_min, gap_max, max_score=11)
            
            # 总分限制在35分以内
            total_arm_score = min(35, left_score + right_score + gap_score)
            
            # 生成反馈（更友好）
            if left_angle < 140:
                feedback.append('⚠️ 左臂可以更伸直一些')
            elif left_angle >= 160:
                feedback.append('✅ 左臂姿势很好')
            
            if right_angle < 140:
                feedback.append('⚠️ 右臂可以更伸直一些')
            elif right_angle >= 160:
                feedback.append('✅ 右臂姿势很好')
            
            if arm_gap < 15:
                feedback.append('⚠️ 双臂可以稍微打开一些')
            elif arm_gap > 50:
                feedback.append('⚠️ 双臂距离略宽，可以收拢一点')
            elif 20 <= arm_gap <= 40:
                feedback.append('✅ 双臂间距标准')
            
            return total_arm_score, feedback
            
        except Exception as e:
            return 0, [f'手臂姿态识别异常: {str(e)}']
    
    def _score_body_v2(self, landmarks, standards):
        """评分身体重心（优化版）"""
        feedback = []
        
        try:
            # 膝盖角度
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
            
            # 使用柔性评分
            knee_min, knee_max = standards["knee_angle_range"]
            
            left_knee_score = self._soft_range_score(left_knee_angle, knee_min, knee_max, max_score=12)
            right_knee_score = self._soft_range_score(right_knee_angle, knee_min, knee_max, max_score=12)
            
            # 重心稳定性（双腿角度差）
            knee_diff = abs(left_knee_angle - right_knee_angle)
            balance_score = max(0, 6 - knee_diff / 10)  # 差异越小越好
            
            # 总分限制在30分以内
            total_body_score = min(30, left_knee_score + right_knee_score + balance_score)
            
            # 生成反馈
            if left_knee_angle > 140:
                feedback.append('⚠️ 左腿可以弯曲一些，降低重心')
            elif left_knee_angle < 50:
                feedback.append('⚠️ 左腿弯曲过多，重心过低')
            else:
                feedback.append('✅ 左腿弯曲适中')
            
            if right_knee_angle > 140:
                feedback.append('⚠️ 右腿可以弯曲一些，降低重心')
            elif right_knee_angle < 50:
                feedback.append('⚠️ 右腿弯曲过多，重心过低')
            else:
                feedback.append('✅ 右腿弯曲适中')
            
            if knee_diff < 15:
                feedback.append('✅ 双腿平衡稳定')
            else:
                feedback.append('⚠️ 注意双腿平衡，保持对称')
            
            return total_body_score, feedback
            
        except Exception as e:
            return 0, [f'身体重心识别异常: {str(e)}']
    
    def _score_position_v2(self, landmarks, standards, body_height):
        """
        评分触球位置（优化版）
        改进：更准确的相对位置计算
        """
        feedback = []
        
        try:
            # 关键高度点
            wrist_y = (landmarks['left_wrist']['y'] + landmarks['right_wrist']['y']) / 2
            shoulder_y = (landmarks['left_shoulder']['y'] + landmarks['right_shoulder']['y']) / 2
            hip_y = (landmarks['left_hip']['y'] + landmarks['right_hip']['y']) / 2
            knee_y = (landmarks['left_knee']['y'] + landmarks['right_knee']['y']) / 2
            
            # 改进的相对位置计算
            # 方法1：手腕相对于髋部的位置
            wrist_hip_ratio = abs(wrist_y - hip_y) / body_height if body_height > 0 else 0
            
            # 方法2：手腕在肩-膝之间的相对位置
            shoulder_knee_range = abs(knee_y - shoulder_y)
            if shoulder_knee_range > 0:
                wrist_position = (wrist_y - shoulder_y) / shoulder_knee_range
            else:
                wrist_position = 0
            
            # 评分：垫球时手腕应该在腰部到膝盖之间（略低于髋部）
            # 理想位置：wrist_position ≈ 0.6-1.2（肩膝之间偏下）
            ideal_min, ideal_max = 0.5, 1.3
            position_score_1 = self._soft_range_score(wrist_position, ideal_min, ideal_max, max_score=15)
            
            # 评分2：手腕不应该太高或太低
            if wrist_y < hip_y:  # 手腕高于髋部
                height_score = max(0, 10 - (hip_y - wrist_y) / body_height * 50)
            else:  # 手腕低于髋部（正常）
                relative_below = (wrist_y - hip_y) / body_height
                if relative_below < 0.3:  # 理想：略低于髋部
                    height_score = 10
                else:  # 太低了
                    height_score = max(0, 10 - (relative_below - 0.3) * 30)
            
            # 总分限制在25分以内
            total_position_score = min(25, position_score_1 + height_score)
            
            # 生成反馈
            if wrist_y < shoulder_y:
                feedback.append('❌ 触球位置过高，应该在腰腹部')
            elif wrist_y > knee_y:
                feedback.append('❌ 触球位置过低，容易失误')
            elif hip_y <= wrist_y <= knee_y:
                feedback.append('✅ 触球位置标准（腰腹前下方）')
            else:
                feedback.append('⚠️ 触球位置略有偏差')
            
            # 前后位置检查（使用z坐标）
            wrist_z = (landmarks['left_wrist']['z'] + landmarks['right_wrist']['z']) / 2
            shoulder_z = (landmarks['left_shoulder']['z'] + landmarks['right_shoulder']['z']) / 2
            
            if abs(wrist_z - shoulder_z) < 0.1:
                feedback.append('✅ 手臂前伸位置合适')
            elif wrist_z < shoulder_z - 0.15:
                feedback.append('⚠️ 手臂可以稍微前伸一些')
            
            return total_position_score, feedback
            
        except Exception as e:
            return 0, [f'触球位置识别异常: {str(e)}']
    
    def _score_stability(self, landmarks):
        """评分整体稳定性"""
        feedback = []
        
        try:
            key_points = ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                         'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
                         'left_knee', 'right_knee']
            
            visibilities = [landmarks[point]['visibility'] for point in key_points]
            avg_visibility = float(np.mean(visibilities))  # 转换为Python float
            
            # 稳定性分数限制在10分以内
            stability_score = float(min(10, avg_visibility * 10))
            
            if avg_visibility > 0.75:
                feedback.append('✅ 姿态识别清晰')
            elif avg_visibility > 0.5:
                feedback.append('⚠️ 姿态识别一般，建议改善拍摄角度')
            else:
                feedback.append('❌ 姿态识别不清晰，请确保全身入镜')
            
            return stability_score, feedback
            
        except Exception as e:
            return 0, [f'稳定性评估异常: {str(e)}']
    
    def _soft_range_score(self, value, min_val, max_val, max_score):
        """
        柔性范围评分（更友好的评分曲线）
        
        在范围内：满分
        略微超出：部分分数（渐变）
        严重超出：低分
        """
        if min_val <= value <= max_val:
            # 在理想范围内，满分
            return max_score
        elif value < min_val:
            # 低于最小值
            deviation = min_val - value
            tolerance = (max_val - min_val) * 0.5  # 容忍度
            score = max(0, max_score * (1 - deviation / tolerance))
            return score
        else:
            # 高于最大值
            deviation = value - max_val
            tolerance = (max_val - min_val) * 0.5
            score = max(0, max_score * (1 - deviation / tolerance))
            return score
    
    def _calculate_smoothness(self, landmarks_sequence):
        """
        计算动作流畅度
        基于关键点的帧间变化率
        """
        if len(landmarks_sequence) < 2:
            return 0.5
        
        try:
            # 选择关键点：手腕、肘、肩
            key_points = ['left_wrist', 'right_wrist', 'left_elbow', 'right_elbow']
            
            # 计算相邻帧的位移
            displacements = []
            for i in range(len(landmarks_sequence) - 1):
                if landmarks_sequence[i] is None or landmarks_sequence[i+1] is None:
                    continue
                
                frame_displacement = 0
                for point in key_points:
                    try:
                        dx = landmarks_sequence[i+1][point]['x'] - landmarks_sequence[i][point]['x']
                        dy = landmarks_sequence[i+1][point]['y'] - landmarks_sequence[i][point]['y']
                        displacement = np.sqrt(dx**2 + dy**2)
                        frame_displacement += displacement
                    except:
                        continue
                
                displacements.append(frame_displacement)
            
            if not displacements:
                return 0.5
            
            # 计算变化的标准差（越小越流畅）
            displacement_std = float(np.std(displacements))  # 转换为Python float
            displacement_mean = float(np.mean(displacements))  # 转换为Python float
            
            # 归一化：变化系数（CV）
            if displacement_mean > 0:
                cv = displacement_std / displacement_mean
            else:
                cv = 0
            
            # 转换为分数（CV越小越好）
            # CV < 0.3: 很流畅
            # CV > 1.0: 很不流畅
            smoothness = float(max(0, min(1, 1 - cv / 0.8)))
            
            return smoothness
            
        except Exception as e:
            return 0.5
    
    def _calculate_completeness(self, landmarks_sequence):
        """
        计算动作完整性
        检查是否包含垫球的关键阶段：准备-接球-缓冲
        """
        if len(landmarks_sequence) < 3:
            return 0.3
        
        try:
            # 提取手腕高度序列
            wrist_heights = []
            for landmarks in landmarks_sequence:
                if landmarks is not None:
                    wrist_y = (landmarks['left_wrist']['y'] + landmarks['right_wrist']['y']) / 2
                    wrist_heights.append(wrist_y)
            
            if len(wrist_heights) < 3:
                return 0.3
            
            wrist_heights = np.array(wrist_heights)
            
            # 检查是否有"下降-上升"的过程（接球-缓冲）
            # 1. 找到最低点
            min_idx = np.argmin(wrist_heights)
            
            # 2. 检查最低点前后是否有变化
            has_descent = False
            has_ascent = False
            
            if min_idx > 0:
                # 前面有下降
                descent = wrist_heights[0] - wrist_heights[min_idx]
                if descent > 0.05:  # 有明显下降
                    has_descent = True
            
            if min_idx < len(wrist_heights) - 1:
                # 后面有上升
                ascent = wrist_heights[-1] - wrist_heights[min_idx]
                if ascent > 0.03:  # 有上升（缓冲）
                    has_ascent = True
            
            # 综合评分
            if has_descent and has_ascent:
                completeness = 1.0
            elif has_descent or has_ascent:
                completeness = 0.7
            else:
                completeness = 0.4
            
            return completeness
            
        except Exception as e:
            return 0.5
    
    def get_grade(self, score):
        """根据分数返回等级（调整后的标准）"""
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

