"""
位置选择组件
显示排球场的6个位置，所有位置均可选择体验
"""
import streamlit as st

def render_position_selector():
    """渲染位置选择页面"""
    st.title("🏐 选择你的位置")
    st.markdown("---")
    
    # 位置定义
    positions = {
        'libero': {
            'name': '自由人',
            'icon': '🛡️',
            'description': '防守核心，专注一传和防守',
            'enabled': True
        },
        'outside': {
            'name': '主攻',
            'icon': '⚡',
            'description': '全能型选手，主要进攻点',
            'enabled': True
        },
        'middle': {
            'name': '副攻',
            'icon': '🧱',
            'description': '快攻和拦网专家',
            'enabled': True
        },
        'setter': {
            'name': '二传',
            'icon': '🎯',
            'description': '场上指挥官，组织进攻',
            'enabled': True
        },
        'opposite': {
            'name': '接应',
            'icon': '💪',
            'description': '进攻终结者',
            'enabled': True
        },
        'defensive': {
            'name': '防守队员',
            'icon': '🦸',
            'description': '后排防守专家',
            'enabled': True
        }
    }
    
    # 使用网格布局 (3列2行)
    st.markdown("### 请选择你要练习的位置：")
    st.markdown("")
    
    # 第一行
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    keys = list(positions.keys())
    for i in range(3):
        with cols[i]:
            key = keys[i]
            pos = positions[key]
            
            # 卡片样式
            if pos['enabled']:
                if st.button(
                    f"{pos['icon']} {pos['name']}\n\n{pos['description']}", 
                    key=f"pos_{key}",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.selected_position = key
                    st.session_state.page = 'practice_selection'
                    st.rerun()
            else:
                st.button(
                    f"{pos['icon']} {pos['name']}\n\n🔒 敬请期待", 
                    key=f"pos_{key}",
                    use_container_width=True,
                    disabled=True
                )
    
    st.markdown("")
    
    # 第二行
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i in range(3, 6):
        with cols[i-3]:
            key = keys[i]
            pos = positions[key]
            
            if pos['enabled']:
                if st.button(
                    f"{pos['icon']} {pos['name']}\n\n{pos['description']}", 
                    key=f"pos_{key}",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.selected_position = key
                    st.session_state.page = 'practice_selection'
                    st.rerun()
            else:
                st.button(
                    f"{pos['icon']} {pos['name']}\n\n🔒 敬请期待", 
                    key=f"pos_{key}",
                    use_container_width=True,
                    disabled=True
                )
    
    st.markdown("---")
    st.info("💡 提示：可以尝试任意位置的训练体验，后续还会不断丰富各位置的专属内容！")

