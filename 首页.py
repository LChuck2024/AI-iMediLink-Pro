# SQLite版本兼容性修复 - 必须在导入任何依赖之前
try:
    import pysqlite3
    import sys
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass

import streamlit as st
from utils.auth_ui import AuthUI
from utils.session_manager import SessionManager

# 设置页面配置
st.set_page_config(
    page_title="医脉通智能诊疗系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 初始化会话管理器和认证UI
session_manager = SessionManager()
auth_ui = AuthUI(session_manager)

# 添加CSS样式
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main > div {
        padding: 1rem 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        margin: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .hero-section {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .hero-content {
        position: relative;
        z-index: 1;
    }
    
    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 300;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    .feature-grid {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        grid-template-rows: repeat(2, 1fr) !important;
        gap: 1.5rem !important;
        margin: 2rem 0;
        width: 100%;
        max-width: none;
    }
    
    @media (max-width: 768px) {
        .feature-grid {
            grid-template-columns: 1fr;
            grid-template-rows: auto;
        }
    }
    
    @media (max-width: 1024px) and (min-width: 769px) {
        .feature-grid {
            grid-template-columns: repeat(2, 1fr);
            grid-template-rows: repeat(3, 1fr);
        }
    }
    
    .feature-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        color: #5a6c7d;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .info-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
        border-left: 5px solid #667eea;
    }
    
    .section-title {
        font-size: 2.5rem;
        font-weight: 600;
        text-align: center;
        color: #2c3e50;
        margin: 3rem 0 2rem 0;
        position: relative;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 2px;
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    .cta-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 3rem 0;
    }
    
    .cta-button {
        background: white;
        color: #667eea;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        display: inline-block;
        margin-top: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #5a6c7d;
        border-top: 1px solid #e9ecef;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# 英雄区域
st.markdown("""
<div class='hero-section'>
    <div class='hero-content'>
        <h1 class='hero-title'>🏥 医脉通智能诊疗系统</h1>
        <p class='hero-subtitle'>基于人工智能的专业医疗咨询平台，为您提供24/7智能医疗服务</p>
        <div class='stats-container'>
            <div class='stat-card'>
                <span class='stat-number'>6+</span>
                <span class='stat-label'>专业科室</span>
            </div>
            <div class='stat-card'>
                <span class='stat-number'>5+</span>
                <span class='stat-label'>AI模型支持</span>
            </div>
            <div class='stat-card'>
                <span class='stat-number'>24/7</span>
                <span class='stat-label'>在线服务</span>
            </div>
            <div class='stat-card'>
                <span class='stat-number'>100%</span>
                <span class='stat-label'>隐私保护</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# st.markdown("""
#     <div class='cta-section'>
#         <h2 style='margin-bottom: 1rem; font-size: 2rem;'>🚀 开始您的智能医疗咨询之旅</h2>
#         <p style='font-size: 1.1rem; margin-bottom: 1rem; opacity: 0.9;'>专业AI助手随时为您提供医疗咨询服务，让健康管理更简单</p>
#         <div style='background: rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>
#             <p style='font-size: 1rem; margin-bottom: 1rem; opacity: 0.9;'>🎭 游客模式：每日1次免费咨询</p>
#             <p style='font-size: 1rem; margin-bottom: 1rem; opacity: 0.9;'>🔐 注册登录：每日5次咨询机会</p>
#             <p style='font-size: 0.9rem; opacity: 0.8;'>登录后您将获得：个性化咨询记录、使用统计、专业建议保存等功能</p>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)


# 用户认证区域
with st.container():
    # 检查登录状态
    is_logged_in = session_manager.is_logged_in()
    user_info = session_manager.get_user_info() if is_logged_in else None
    
    if is_logged_in:
        # 显示用户信息和登出按钮
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"欢迎回来，{user_info['username']}！")
            remaining_time = session_manager.get_remaining_time()

            if remaining_time > 0:
                st.info(f"自动登录剩余时间：{remaining_time} 分钟")
        with col2:
            if st.button("登出", key="logout_btn"):
                session_manager.logout()
                st.rerun()
    else:
        # 显示登录界面
        is_logged_in, user_info = auth_ui.render_auth_interface()

# 行动号召区域
if is_logged_in:
    # 已登录用户显示正常的咨询按钮
    st.markdown("""
    <div class='cta-section'>
        <h2 style='margin-bottom: 1rem; font-size: 2rem;'>🚀 开始您的智能医疗咨询之旅</h2>
        <p style='font-size: 1.1rem; margin-bottom: 2rem; opacity: 0.9;'>专业AI助手随时为您提供医疗咨询服务，让健康管理更简单</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用Streamlit按钮进行页面切换
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 立即开始咨询 →", key="start_consultation_footer", use_container_width=True, type="primary"):
              st.switch_page("pages/1_医脉通.py")

# 项目简介
st.markdown("""
<div class='info-card'>
    <h2>🎯 系统简介</h2>
    <p>医脉通智能诊疗系统是一个基于人工智能的医疗咨询平台，提供多科室智能助手服务。通过集成多种大模型和检索增强生成技术，为用户提供专业、高效、个性化的医疗咨询服务。我们致力于让每个人都能享受到高质量的医疗咨询服务，无论何时何地。</p>
</div>
""", unsafe_allow_html=True)

# 功能特点
st.markdown("<h2 class='section-title'>✨ 核心功能</h2>", unsafe_allow_html=True)

features = [
    {
        "icon": "🏥",
        "title": "多科室智能助手",
        "description": "覆盖男科、内科、妇产科、肿瘤科、儿科、外科等多个专业科室，每个科室都配备专业的AI助手，提供针对性的医疗咨询服务。"
    },
    {
        "icon": "🤖",
        "title": "多模型智能引擎",
        "description": "集成DeepSeek、Qwen、Hunyuan等多种先进大模型，确保回答的准确性和专业性，用户可根据需求选择最适合的模型。"
    },
    {
        "icon": "🔍",
        "title": "检索增强生成",
        "description": "采用RAG技术，结合专业医学知识库，优先从权威医学资料中提取信息，确保回答的科学性和可靠性。"
    },
    {
        "icon": "💬",
        "title": "实时流式对话",
        "description": "支持流式输出，实时显示AI思考和回答过程，提供更自然的对话体验，减少用户等待时间。"
    },
    {
        "icon": "🔧",
        "title": "个性化配置",
        "description": "支持用户自定义模型参数，包括温度调节、最大Token数设置等，满足不同用户的个性化需求。"
    },
    {
        "icon": "🔒",
        "title": "隐私安全保护",
        "description": "严格遵循医疗数据保护标准，所有对话内容本地处理，确保用户隐私和医疗信息的绝对安全。"
    }
]

st.markdown("""
<div class='feature-grid'>
""", unsafe_allow_html=True)

for feature in features:
    st.markdown(f"""
    <div class='feature-card'>
        <span class='feature-icon'>{feature['icon']}</span>
        <h3 class='feature-title'>{feature['title']}</h3>
        <p class='feature-description'>{feature['description']}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# 使用说明
st.markdown("<h2 class='section-title'>📖 使用指南</h2>", unsafe_allow_html=True)

st.markdown("""
<div class='info-card'>
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-top: 1rem;'>
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 2.5rem; margin-bottom: 1rem;'>🏥</div>
            <h3 style='color: #2c3e50; margin-bottom: 0.5rem;'>选择科室</h3>
            <p style='color: #5a6c7d; font-size: 0.9rem;'>根据您的需求选择相应的专业科室</p>
        </div>
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 2.5rem; margin-bottom: 1rem;'>💬</div>
            <h3 style='color: #2c3e50; margin-bottom: 0.5rem;'>描述症状</h3>
            <p style='color: #5a6c7d; font-size: 0.9rem;'>详细描述您的症状或医疗问题</p>
        </div>
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 2.5rem; margin-bottom: 1rem;'>🤖</div>
            <h3 style='color: #2c3e50; margin-bottom: 0.5rem;'>获得建议</h3>
            <p style='color: #5a6c7d; font-size: 0.9rem;'>AI助手提供专业的医疗建议和指导</p>
        </div>
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 2.5rem; margin-bottom: 1rem;'>⚙️</div>
            <h3 style='color: #2c3e50; margin-bottom: 0.5rem;'>个性配置</h3>
            <p style='color: #5a6c7d; font-size: 0.9rem;'>根据需要调整模型参数和设置</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 科室介绍
st.markdown("<h2 class='section-title'>🏥 专业科室</h2>", unsafe_allow_html=True)

departments = [
    {"name": "内科", "icon": "🫀", "desc": "心血管、呼吸系统、消化系统等内科疾病咨询"},
    {"name": "外科", "icon": "🔬", "desc": "外科手术、创伤处理、术后护理等专业指导"},
    {"name": "妇产科", "icon": "👶", "desc": "妇科疾病、孕期保健、产后护理等专业服务"},
    {"name": "儿科", "icon": "🧸", "desc": "儿童健康、生长发育、疫苗接种等专业咨询"},
    {"name": "肿瘤科", "icon": "🎗️", "desc": "肿瘤筛查、治疗方案、康复指导等专业建议"},
    {"name": "男科", "icon": "👨‍⚕️", "desc": "男性健康、生殖系统、泌尿系统等专业服务"}
]

col1, col2, col3 = st.columns(3)
for i, dept in enumerate(departments):
    with [col1, col2, col3][i % 3]:
        st.markdown(f"""
        <div style='background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;
                    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); text-align: center;
                    transition: transform 0.3s ease;'>
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{dept['icon']}</div>
            <h4 style='color: #2c3e50; margin-bottom: 0.5rem;'>{dept['name']}</h4>
            <p style='color: #5a6c7d; font-size: 0.85rem; line-height: 1.4;'>{dept['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

# 免责声明
st.markdown("""
<div class='info-card' style='background: #fff3cd; border-left: 5px solid #ffc107;'>
    <h3 style='color: #856404; margin-bottom: 1rem;'>⚠️ 重要提示</h3>
    <p style='color: #856404; font-size: 0.9rem; line-height: 1.6;'>
        本系统提供的医疗建议仅供参考，不能替代专业医生的诊断和治疗。如有严重症状或紧急情况，请立即就医。
        使用本系统即表示您同意我们的服务条款和隐私政策。
    </p>
</div>
""", unsafe_allow_html=True)

# 项目信息
st.markdown("""
<div class='footer'>
    <p>© 2025 AIE直通车 | Powered by AIE-52 G5</p>
    <p style='font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.7;'>致力于让AI技术服务于人类健康事业</p>
</div>
""", unsafe_allow_html=True)
