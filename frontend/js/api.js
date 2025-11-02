/**
 * API通信模块
 * 处理与后端Flask API的所有HTTP请求
 */

const API_BASE_URL = 'http://localhost:5000/api';

class VolleyballAPI {
    /**
     * 上传视频并分析
     * @param {File} videoFile - 视频文件对象
     * @param {string} mode - 分析模式 ('single' 或 'sequence')
     * @returns {Promise<Object>} 分析结果
     */
    async analyzeVideo(videoFile, mode = 'single') {
        const formData = new FormData();
        formData.append('video', videoFile);
        formData.append('mode', mode);
        
        try {
            // 设置超时时间：统一为2分钟
            const timeout = 120000; // 2分钟
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            
            const response = await fetch(`${API_BASE_URL}/analyze/video`, {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('视频分析失败:', error);
            
            if (error.name === 'AbortError') {
                return {
                    success: false,
                    error: `请求超时。${mode === 'sequence' ? '连续帧分析' : '单帧分析'}时间过长，请尝试使用更短的视频。`
                };
            }
            
            return {
                success: false,
                error: `网络错误: ${error.message}`
            };
        }
    }
    
    /**
     * 生成可视化视频
     * @param {File} videoFile - 视频文件对象
     * @param {string} visType - 可视化类型
     * @returns {Promise<Object>} 生成结果
     */
    async visualizeVideo(videoFile, visType = 'overlay') {
        const formData = new FormData();
        formData.append('video', videoFile);
        formData.append('vis_type', visType);
        
        try {
            // 增加超时时间到5分钟（视频生成需要较长时间）
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 300000); // 5分钟超时
            
            const response = await fetch(`${API_BASE_URL}/visualize/video`, {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('可视化生成失败:', error);
            
            if (error.name === 'AbortError') {
                return {
                    success: false,
                    error: '请求超时（超过5分钟）。请尝试使用更短的视频。'
                };
            }
            
            return {
                success: false,
                error: `网络错误: ${error.message}`
            };
        }
    }
    
    /**
     * 获取战术题库
     * @returns {Promise<Object>} 题库数据
     */
    async getTacticsQuestions() {
        try {
            const response = await fetch(`${API_BASE_URL}/tactics/questions`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('获取题库失败:', error);
            return {
                error: `网络错误: ${error.message}`
            };
        }
    }
    
    /**
     * 健康检查
     * @returns {Promise<Object>} 服务器状态
     */
    async healthCheck() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('健康检查失败:', error);
            return {
                status: 'error',
                error: error.message
            };
        }
    }
}

// 创建全局API实例
const api = new VolleyballAPI();

