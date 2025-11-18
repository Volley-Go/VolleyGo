"""评分卡片组件"""
import streamlit as st
import plotly.graph_objects as go


def render_score_card(score_summary):
    """
    渲染评分卡片
    
    Args:
        score_summary: 评分摘要字典
    """
    if not score_summary:
        st.warning("暂无评分数据")
        return
    
    total_score = score_summary.get("total_score", 0)
    level_info = score_summary.get("level_info", {})
    
    # 总分展示
    st.markdown("""
        <style>
        .score-container {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            color: white;
            margin: 1rem 0;
        }
        .total-score {
            font-size: 4rem;
            font-weight: bold;
            margin: 0;
        }
        .score-label {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="score-container">
            <div class="total-score">{total_score}</div>
            <div class="score-label">总分 / 100</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 关卡信息
    if level_info.get("passed"):
        st.success(level_info.get("message", "恭喜通过！"))
    else:
        st.info(level_info.get("message", "继续努力！"))
    
    # 分项得分
    st.subheader("📊 分项得分")
    
    # 获取满分信息
    max_scores = score_summary.get('max_scores', {})
    arm_max = max_scores.get('arm_max', 32)
    body_max = max_scores.get('body_max', 33)
    position_max = max_scores.get('position_max', 25)
    stability_max = max_scores.get('stability_max', 10)
    ball_max = max_scores.get('ball_max', 25)
    
    col1, col2 = st.columns(2)
    
    with col1:
        arm_score = score_summary.get('arm_score', 0)
        st.metric("手臂姿态", f"{arm_score:.1f}/{arm_max}")
        st.progress(arm_score / arm_max if arm_max > 0 else 0)
        
        position_score = score_summary.get('position_score', 0)
        st.metric("触球位置", f"{position_score:.1f}/{position_max}")
        st.progress(position_score / position_max if position_max > 0 else 0)
    
    with col2:
        body_score = score_summary.get('body_score', 0)
        st.metric("身体重心", f"{body_score:.1f}/{body_max}")
        st.progress(body_score / body_max if body_max > 0 else 0)
        
        stability_score = score_summary.get('stability_score', 0)
        st.metric("整体稳定", f"{stability_score:.1f}/{stability_max}")
        st.progress(stability_score / stability_max if stability_max > 0 else 0)
    
    # 如果有人球位置评分（有球模式）
    if score_summary.get('ball_score', 0) > 0:
        st.markdown("---")
        ball_score = score_summary.get('ball_score', 0)
        st.metric("人球位置", f"{ball_score:.1f}/{ball_max}")
        st.progress(ball_score / ball_max if ball_max > 0 else 0)
    
    # 雷达图
    render_radar_chart(score_summary)
    
    # 反馈建议
    st.subheader("💡 改进建议")
    feedback = score_summary.get("feedback", [])
    for msg in feedback:
        st.info(msg)


def render_radar_chart(score_summary):
    """
    渲染雷达图
    
    Args:
        score_summary: 评分摘要
    """
    # 获取满分信息
    max_scores = score_summary.get('max_scores', {})
    arm_max = max_scores.get('arm_max', 32)
    body_max = max_scores.get('body_max', 33)
    position_max = max_scores.get('position_max', 25)
    stability_max = max_scores.get('stability_max', 10)
    
    categories = ['手臂姿态', '身体重心', '触球位置', '整体稳定']
    values = [
        (score_summary.get('arm_score', 0) / arm_max) * 100 if arm_max > 0 else 0,
        (score_summary.get('body_score', 0) / body_max) * 100 if body_max > 0 else 0,
        (score_summary.get('position_score', 0) / position_max) * 100 if position_max > 0 else 0,
        (score_summary.get('stability_score', 0) / stability_max) * 100 if stability_max > 0 else 0,
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # 闭合图形
        theta=categories + [categories[0]],
        fill='toself',
        name='得分',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=80, r=80, t=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_simple_score(score_result):
    """
    渲染简单评分（无详细分析）
    
    Args:
        score_result: 评分结果字典
    """
    if not score_result:
        return
    
    total_score = score_result.get("total_score", 0)
    
    # 使用进度条显示
    st.markdown("### 总分")
    st.progress(total_score / 100)
    st.markdown(f"**{total_score} / 100**")
    
    # 显示反馈
    feedback = score_result.get("feedback", [])
    if feedback:
        st.markdown("### 反馈")
        for msg in feedback:
            st.write(f"• {msg}")

