# 管理员后台页面
try:
    import pysqlite3
    import sys
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.user_manager import UserManager
import hashlib

# 设置页面配置
st.set_page_config(
    page_title="管理员后台",
    page_icon="👨‍💼",
    layout="wide"
)

# 管理员认证配置
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()  # 默认密码：admin123

def admin_login():
    """管理员登录界面"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 3rem; border-radius: 20px; margin-bottom: 2rem; color: white; text-align: center;'>
        <h1 style='margin: 0; font-size: 2.5rem;'>👨‍💼 管理员后台</h1>
        <p style='margin: 1rem 0 0 0; opacity: 0.9; font-size: 1.1rem;'>系统管理与数据分析中心</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 15px; 
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); margin: 2rem 0;'>
                <h3 style='text-align: center; color: #2c3e50; margin-bottom: 2rem;'>🔐 管理员登录</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("admin_login_form"):
                username = st.text_input("👤 管理员账号", placeholder="请输入管理员账号")
                password = st.text_input("🔒 管理员密码", type="password", placeholder="请输入管理员密码")
                
                col_login, col_info = st.columns([1, 1])
                
                with col_login:
                    login_clicked = st.form_submit_button("🚀 登录后台", use_container_width=True)
                
                with col_info:
                    st.info("默认账号：admin\n默认密码：admin123")
                
                if login_clicked:
                    if username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
                        st.session_state.admin_logged_in = True
                        st.session_state.admin_username = username
                        st.success("✅ 登录成功！正在跳转到管理后台...")
                        st.rerun()
                    else:
                        st.error("❌ 账号或密码错误，请重试")

def admin_dashboard():
    """管理员仪表板"""
    user_manager = UserManager()
    
    # 页面标题
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white;'>
            <h1 style='margin: 0; font-size: 2rem;'>📊 管理员仪表板</h1>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>欢迎回来，{}</p>
        </div>
        """.format(st.session_state.admin_username), unsafe_allow_html=True)
    
    with col2:
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.session_state.admin_username = None
            st.rerun()
    
    # 获取统计数据
    stats = user_manager.get_admin_statistics()
    
    # 关键指标卡片
    st.markdown("### 📈 关键指标")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.5rem; border-radius: 10px; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 2rem;'>{}</h3>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>总用户数</p>
        </div>
        """.format(stats['total_users']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                    padding: 1.5rem; border-radius: 10px; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 2rem;'>{}</h3>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>付费用户</p>
        </div>
        """.format(stats['premium_users']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 1.5rem; border-radius: 10px; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 2rem;'>{}</h3>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>今日活跃</p>
        </div>
        """.format(stats['today_active']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    padding: 1.5rem; border-radius: 10px; color: #2c3e50; text-align: center;'>
            <h3 style='margin: 0; font-size: 2rem;'>¥{:.0f}</h3>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.8;'>总收入</p>
        </div>
        """.format(stats['total_revenue']), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 用户列表和付费情况
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 👥 用户管理")
        
        # 获取用户列表
        users_data = user_manager.get_all_users_info()
        
        if users_data:
            df = pd.DataFrame(users_data)
            
            # 添加筛选选项
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                user_type_filter = st.selectbox("用户类型筛选", ["全部", "free", "premium", "enterprise"])
            with filter_col2:
                search_user = st.text_input("搜索用户", placeholder="输入用户名或邮箱")
            
            # 应用筛选
            filtered_df = df.copy()
            if user_type_filter != "全部":
                filtered_df = filtered_df[filtered_df['user_type'] == user_type_filter]
            if search_user:
                filtered_df = filtered_df[
                    (filtered_df['username'].str.contains(search_user, case=False, na=False)) |
                    (filtered_df['email'].str.contains(search_user, case=False, na=False))
                ]
            
            # 显示用户表格
            st.dataframe(
                filtered_df,
                use_container_width=True,
                column_config={
                    "id": "ID",
                    "username": "用户名",
                    "email": "邮箱",
                    "user_type": st.column_config.TextColumn(
                        "用户类型"
                    ),
                    "created_at": st.column_config.DatetimeColumn(
                        "注册时间",
                        format="YYYY-MM-DD HH:mm"
                    ),
                    "last_login": st.column_config.DatetimeColumn(
                        "最后登录",
                        format="YYYY-MM-DD HH:mm"
                    ),
                    "total_usage": "总使用次数",
                    "today_usage": "今日已用",
                    "daily_limit": "每日限制",
                    "remaining_usage": "今日剩余"
                }
            )
        else:
            st.info("暂无用户数据")
    
    with col2:
        st.markdown("### 💰 付费统计")
        
        # 用户类型分布饼图
        if 'user_type_stats' in stats:
            fig_pie = px.pie(
                values=list(stats['user_type_stats'].values()),
                names=list(stats['user_type_stats'].keys()),
                title="用户类型分布",
                color_discrete_map={
                    'free': '#ff9999',
                    'premium': '#66b3ff',
                    'enterprise': '#99ff99'
                }
            )
            fig_pie.update_layout(height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # 收入趋势
        st.markdown("#### 📈 收入趋势")
        revenue_data = user_manager.get_revenue_trend()
        if revenue_data:
            df_revenue = pd.DataFrame(revenue_data)
            fig_line = px.line(
                df_revenue, 
                x='date', 
                y='revenue',
                title="近30天收入趋势",
                markers=True
            )
            fig_line.update_layout(height=250)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("暂无收入数据")
    
    st.markdown("---")
    
    # 使用情况分析
    st.markdown("### 📊 使用情况分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 每日使用量趋势
        usage_data = user_manager.get_usage_trend()
        if usage_data:
            df_usage = pd.DataFrame(usage_data)
            fig_usage = px.bar(
                df_usage,
                x='date',
                y='usage_count',
                title="近7天使用量趋势",
                color='usage_count',
                color_continuous_scale='Blues'
            )
            fig_usage.update_layout(height=300)
            st.plotly_chart(fig_usage, use_container_width=True)
        else:
            st.info("暂无使用数据")
    
    with col2:
        # 科室使用分布
        dept_data = user_manager.get_department_usage()
        if dept_data:
            df_dept = pd.DataFrame(dept_data)
            fig_dept = px.bar(
                df_dept,
                x='department',
                y='usage_count',
                title="科室使用分布",
                color='usage_count',
                color_continuous_scale='Greens'
            )
            fig_dept.update_layout(height=300)
            st.plotly_chart(fig_dept, use_container_width=True)
        else:
            st.info("暂无科室使用数据")
    
    # 付费记录详情
    st.markdown("### 💳 付费记录")
    payment_records = user_manager.get_payment_records()
    
    if payment_records:
        df_payments = pd.DataFrame(payment_records)
        st.dataframe(
            df_payments,
            use_container_width=True,
            column_config={
                "id": "记录ID",
                "username": "用户名",
                "plan_type": "套餐类型",
                "amount": st.column_config.NumberColumn(
                    "金额",
                    format="¥%.2f"
                ),
                "payment_method": "支付方式",
                "payment_status": "支付状态",
                "start_date": st.column_config.DatetimeColumn(
                    "开始时间",
                    format="YYYY-MM-DD"
                ),
                "end_date": st.column_config.DatetimeColumn(
                    "结束时间",
                    format="YYYY-MM-DD"
                ),
                "created_at": st.column_config.DatetimeColumn(
                    "创建时间",
                    format="YYYY-MM-DD HH:mm"
                )
            }
        )
    else:
        st.info("暂无付费记录")

# 主程序
def main():
    # 检查管理员登录状态
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if not st.session_state.admin_logged_in:
        admin_login()
    else:
        admin_dashboard()

if __name__ == "__main__":
    main()