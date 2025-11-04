/**
 * API通信模块
 * 处理与后端Flask API的所有HTTP请求
 */

// 使用相对路径，自动适配当前域名（本地开发或服务器部署）
const API_BASE_URL = '/api';

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
     * 测试AI教练服务状态
     * @returns {Promise<Object>} 服务状态
     */
    async testAICoach() {
        try {
            const response = await fetch(`${API_BASE_URL}/ai-coach/test`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('AI服务测试失败:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    /**
     * AI教练智能问答
     * @param {string} question - 用户问题
     * @returns {Promise<Object>} AI回答
     */
    async askAICoach(question) {
        try {
            const response = await fetch(`${API_BASE_URL}/ai-coach/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('AI问答失败:', error);
            
            // 如果是503错误，尝试诊断
            if (error.message.includes('503') || error.message.includes('暂不可用')) {
                console.log('🔍 尝试诊断AI服务...');
                const testResult = await this.testAICoach();
                console.log('诊断结果:', testResult);
                
                if (testResult.success && testResult.status) {
                    const status = testResult.status;
                    if (!status.openai_available) {
                        return {
                            success: false,
                            error: 'OpenAI库未安装。请在Flask服务器终端运行: pip install openai>=1.0.0'
                        };
                    }
                    if (!status.client_initialized) {
                        return {
                            success: false,
                            error: 'OpenAI客户端初始化失败。请检查Flask服务器终端的错误信息'
                        };
                    }
                    if (!status.api_key_set) {
                        return {
                            success: false,
                            error: 'API密钥未配置。请检查 backend/api/flask_api.py 中的配置'
                        };
                    }
                    if (!status.base_url_set) {
                        return {
                            success: false,
                            error: 'API URL未配置。请检查 backend/api/flask_api.py 中的配置'
                        };
                    }
                }
            }
            
            return {
                success: false,
                error: error.message
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

