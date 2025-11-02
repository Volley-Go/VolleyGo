"""
Flask REST API for Volleyball Training System
提供HTTP接口供前端调用
"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
import tempfile
import base64
import cv2
import numpy as np

# ChatGPT API配置
try:
    from openai import OpenAI
    import httpx
    
    # 配置ChatGPT API
    API_BASE_URL = "https://api.chatanywhere.tech"
    API_KEY = "sk-dPxOakeokunQGR0YcbWLi03gOn9K00DRmTjlfHcCP9WvRKh0"
    
    os.environ["OPENAI_API_KEY"] = API_KEY
    os.environ["OPENAI_BASE_URL"] = API_BASE_URL
    
    # 创建自定义HTTP客户端，解决Windows连接问题
    # 使用更宽松的配置来避免WinError 6
    # 注意：在Windows上，使用更保守的连接池设置
    http_client = httpx.Client(
        timeout=httpx.Timeout(30.0, connect=15.0),
        verify=True,
        limits=httpx.Limits(
            max_connections=5,  # 减少连接数，避免句柄问题
            max_keepalive_connections=2
        ),
        # 不使用HTTPTransport，使用默认transport，更稳定
    )
    
    # 初始化OpenAI客户端，使用自定义HTTP客户端
    openai_client = OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL,
        http_client=http_client,
        timeout=30.0,
        max_retries=2  # 减少重试次数，使用自定义HTTP客户端的重试
    )
    OPENAI_AVAILABLE = True
    print(f"✅ ChatGPT API已配置: {API_BASE_URL}")
except ImportError as e:
    print(f"警告: 必需的库未安装: {e}")
    print("请运行: pip install openai httpx")
    openai_client = None
    OPENAI_AVAILABLE = False
except Exception as e:
    print(f"❌ ChatGPT API初始化失败: {str(e)}")
    import traceback
    traceback.print_exc()
    openai_client = None
    OPENAI_AVAILABLE = False

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.api.volleyball_api import VolleyballAPI
from backend.services.volleyball_service import VolleyballService
from config.settings import OUTPUT_DIR

# 创建Flask应用
app = Flask(__name__, 
            static_folder='../../frontend',
            static_url_path='')
CORS(app)  # 允许跨域请求

# 初始化API
volleyball_api = VolleyballAPI()
volleyball_service = VolleyballService(use_v2_scorer=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """主页 - 返回前端HTML"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': 'Volleyball AI Training System API is running',
        'version': '1.0.0'
    })


@app.route('/api/analyze/video', methods=['POST'])
def analyze_video():
    """
    分析视频接口
    接收上传的视频文件，返回AI分析结果
    """
    try:
        # 检查是否有文件
        if 'video' not in request.files:
            return jsonify({
                'success': False,
                'error': '请上传视频文件'
            }), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '不支持的文件格式，请上传MP4、AVI、MOV或MKV格式'
            }), 400
        
        # 获取分析模式
        analysis_mode = request.form.get('mode', 'single')
        
        # 保存上传的文件到临时目录
        filename = secure_filename(file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        file.save(temp_path)
        
        try:
            # 调用服务分析视频
            result = volleyball_service.analyze_video(temp_path, mode=analysis_mode)
            
            # 将图像转换为base64 - 添加类型检查
            if result.get('pose_image') is not None:
                pose_img = result['pose_image']
                # 确保是numpy array
                if isinstance(pose_img, np.ndarray) and pose_img.size > 0:
                    try:
                        pose_img_rgb = cv2.cvtColor(pose_img, cv2.COLOR_BGR2RGB)
                        _, buffer = cv2.imencode('.jpg', pose_img_rgb)
                        pose_img_base64 = base64.b64encode(buffer).decode('utf-8')
                        result['pose_image_base64'] = pose_img_base64
                    except Exception as e:
                        print(f"警告：姿态图像转换失败: {str(e)}")
                # 删除numpy array，不能JSON序列化
                if 'pose_image' in result:
                    del result['pose_image']
            
            # 处理landmarks，转换为可序列化格式
            if result.get('landmarks') is not None:
                result['landmarks'] = str(result['landmarks'])
            
            # 处理轨迹图 - 添加类型检查
            if result.get('trajectory_plot') is not None:
                traj_img = result['trajectory_plot']
                # 确保是numpy array
                if isinstance(traj_img, np.ndarray) and traj_img.size > 0:
                    try:
                        traj_img_rgb = cv2.cvtColor(traj_img, cv2.COLOR_BGR2RGB)
                        _, buffer = cv2.imencode('.jpg', traj_img_rgb)
                        traj_img_base64 = base64.b64encode(buffer).decode('utf-8')
                        result['trajectory_plot_base64'] = traj_img_base64
                    except Exception as e:
                        print(f"警告：轨迹图像转换失败: {str(e)}")
                # 删除numpy array
                if 'trajectory_plot' in result:
                    del result['trajectory_plot']
            
            # 处理annotated_frames（序列分析模式下可能有多个帧）
            if result.get('annotated_frames') is not None:
                # 只保留最佳帧
                if isinstance(result['annotated_frames'], list) and len(result['annotated_frames']) > 0:
                    best_idx = result.get('best_frame_idx', 0)
                    if best_idx < len(result['annotated_frames']):
                        best_frame = result['annotated_frames'][best_idx]
                        if isinstance(best_frame, np.ndarray) and best_frame.size > 0:
                            try:
                                best_frame_rgb = cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB)
                                _, buffer = cv2.imencode('.jpg', best_frame_rgb)
                                result['pose_image_base64'] = base64.b64encode(buffer).decode('utf-8')
                            except:
                                pass
                # 删除annotated_frames
                if 'annotated_frames' in result:
                    del result['annotated_frames']
            
            return jsonify(result)
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/visualize/video', methods=['POST'])
def visualize_video():
    """
    生成可视化视频接口
    支持4种可视化类型：overlay, skeleton, comparison, trajectory
    
    注意：这是一个长时间操作，可能需要1-3分钟
    """
    try:
        if 'video' not in request.files:
            return jsonify({
                'success': False,
                'error': '请上传视频文件'
            }), 400
        
        file = request.files['video']
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '不支持的文件格式'
            }), 400
        
        # 获取可视化类型
        vis_type = request.form.get('vis_type', 'overlay')
        
        # 验证可视化类型
        valid_types = ['overlay', 'skeleton', 'comparison', 'trajectory']
        if vis_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'不支持的可视化类型。支持: {", ".join(valid_types)}'
            }), 400
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        temp_input = os.path.join(tempfile.gettempdir(), filename)
        file.save(temp_input)
        
        # 生成输出文件名
        output_filename = f"vis_{vis_type}_{filename}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        try:
            print(f"🎬 开始生成{vis_type}可视化视频...")
            print(f"📁 输入: {temp_input}")
            print(f"📁 输出: {output_path}")
            
            # 生成可视化视频
            result = volleyball_service.generate_visualization_video(
                video_path=temp_input,
                output_path=output_path,
                vis_type=vis_type
            )
            
            print(f"✅ 生成完成: {result.get('success', False)}")
            
            if result['success']:
                # 检查文件是否真的生成了
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / (1024 * 1024)
                    print(f"📦 文件大小: {file_size:.2f} MB")
                    
                    return jsonify({
                        'success': True,
                        'video_url': f'/api/output/{output_filename}',
                        'filename': output_filename,
                        'vis_type': vis_type,
                        'file_size_mb': round(file_size, 2)
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '视频生成成功但文件未找到'
                    }), 500
            else:
                return jsonify(result), 500
                
        except Exception as e:
            print(f"❌ 生成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'生成失败: {str(e)}'
            }), 500
        finally:
            if os.path.exists(temp_input):
                try:
                    os.remove(temp_input)
                    print(f"🗑️ 清理临时文件: {temp_input}")
                except:
                    pass
    
    except Exception as e:
        print(f"❌ 请求处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/output/<filename>')
def get_output_file(filename):
    """获取输出文件"""
    try:
        return send_from_directory(OUTPUT_DIR, filename)
    except:
        return jsonify({'error': '文件不存在'}), 404


@app.route('/api/tactics/questions', methods=['GET'])
def get_tactics_questions():
    """获取战术题库"""
    import json
    tactics_file = Path('data/tactics_questions.json')
    
    if tactics_file.exists():
        with open(tactics_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({
            'error': '题库文件不存在'
        }), 404


@app.route('/api/score/summary', methods=['POST'])
def get_score_summary():
    """获取评分摘要"""
    try:
        score_result = request.json
        summary = volleyball_api.get_score_summary(score_result)
        return jsonify(summary)
    except Exception as e:
        return jsonify({
            'error': f'获取评分摘要失败: {str(e)}'
        }), 500


@app.route('/api/ai-coach/ask', methods=['POST'])
def ai_coach_ask():
    """
    AI教练智能问答接口
    接收用户问题，返回AI回答
    """
    try:
        # 详细检查OpenAI可用性
        if not OPENAI_AVAILABLE:
            print("❌ OpenAI库未安装")
            return jsonify({
                'success': False,
                'error': 'OpenAI库未安装，请运行: pip install openai>=1.0.0'
            }), 503
        
        if not openai_client:
            print("❌ OpenAI客户端未初始化")
            return jsonify({
                'success': False,
                'error': 'OpenAI客户端初始化失败，请检查API配置'
            }), 503
        
        # 检查API密钥和URL
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL")
        
        if not api_key:
            print("❌ OPENAI_API_KEY未设置")
            return jsonify({
                'success': False,
                'error': 'API密钥未配置'
            }), 503
        
        if not base_url:
            print("❌ OPENAI_BASE_URL未设置")
            return jsonify({
                'success': False,
                'error': 'API URL未配置'
            }), 503
        
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '请输入问题'
            }), 400
        
        print(f"📝 收到问题: {question}")
        print(f"🔑 API Key: {api_key[:10]}...")
        print(f"🌐 Base URL: {base_url}")
        
        # 构建系统提示词，让AI专注于排球相关回答
        system_prompt = """你是一位专业的排球教练和训练专家。你的职责是：
1. 回答关于排球技术、战术、训练方法的问题
2. 提供专业、详细、易懂的解答
3. 根据用户水平给出合适的建议
4. 用中文回答，语言要友好、鼓励性
5. 如果问题与排球无关，礼貌地引导用户提问排球相关问题

请始终保持专业、友好、鼓励的态度。"""
        
        # 调用ChatGPT API
        try:
            print("🚀 开始调用ChatGPT API...")
            print(f"📍 目标URL: {API_BASE_URL}")
            
            # 测试网络连接
            import socket
            try:
                host = API_BASE_URL.replace("https://", "").replace("http://", "").split("/")[0]
                print(f"🔍 测试连接到: {host}")
                socket.create_connection((host, 443), timeout=5)
                print("✅ 网络连接正常")
            except Exception as conn_err:
                print(f"⚠️ 网络连接测试失败: {conn_err}")
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # ChatGPT模型
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            print(f"✅ API调用成功")
            answer = response.choices[0].message.content.strip()
            print(f"📄 回答长度: {len(answer)} 字符")
            
            return jsonify({
                'success': True,
                'answer': answer,
                'question': question
            })
            
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            print(f"❌ ChatGPT API调用失败: {error_msg}")
            print(f"错误类型: {error_type}")
            import traceback
            traceback.print_exc()
            
            # 提供更详细的错误信息和解决建议
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                error_detail = "API密钥无效，请检查密钥是否正确"
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                error_detail = "请求频率过高，请稍后再试"
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                error_detail = "请求超时，请检查网络连接或稍后再试"
            elif "connection" in error_msg.lower() or "WinError" in error_msg or "APIConnectionError" in error_type:
                error_detail = f"网络连接失败。可能原因：\n1. 网络连接问题 - 请检查是否能访问 {API_BASE_URL}\n2. 防火墙/代理设置 - 可能阻止了连接\n3. Windows网络问题 - 尝试重启网络适配器\n4. VPN/代理冲突 - 尝试关闭VPN或调整代理设置\n\n错误详情: {error_msg}"
            elif "ssl" in error_msg.lower() or "certificate" in error_msg.lower():
                error_detail = "SSL证书验证失败，请检查网络环境或代理设置"
            else:
                error_detail = f"API调用失败: {error_msg}"
            
            return jsonify({
                'success': False,
                'error': error_detail
            }), 500
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 智能问答接口错误: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'服务器错误: {error_msg}'
        }), 500


@app.route('/api/ai-coach/test', methods=['GET'])
def test_ai_coach():
    """
    测试AI教练服务是否可用
    """
    try:
        status = {
            'openai_available': OPENAI_AVAILABLE,
            'client_initialized': openai_client is not None,
            'api_key_set': bool(os.environ.get("OPENAI_API_KEY")),
            'base_url_set': bool(os.environ.get("OPENAI_BASE_URL")),
            'api_key_preview': os.environ.get("OPENAI_API_KEY", "")[:10] + "..." if os.environ.get("OPENAI_API_KEY") else "未设置",
            'base_url': os.environ.get("OPENAI_BASE_URL", "未设置")
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    
    # 启动Flask服务器
    print("🏐 Volleyball AI Training System API Server")
    print("=" * 50)
    print(f"📍 Server running on: http://localhost:5000")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

