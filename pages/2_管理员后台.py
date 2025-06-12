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
from utils.session_manager import SessionManager

# 设置页面配置
st.set_page_config(
    page_title="医脉通管理后台",
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话管理器
session_manager = SessionManager()

# 检查用户权限 - 只允许管理员访问
if session_manager.is_logged_in():
    user_info = session_manager.get_user_info()
    if user_info and user_info.get('user_type') != 'admin':
        st.error("⛔ 权限不足，您没有访问管理后台的权限")
        st.warning("只有管理员用户才能访问此页面")
        
        # 提供返回首页的按钮
        if st.button("返回首页"):
            st.switch_page("首页.py")
        
        # 停止页面的进一步执行
        st.stop()
else:
    st.error("⛔ 请先登录")
    st.warning("您需要以管理员身份登录才能访问此页面")
    
    # 提供返回首页的按钮
    if st.button("返回首页"):
        st.switch_page("首页.py")
    
    # 停止页面的进一步执行
    st.stop()

# 自定义CSS样式
st.markdown("""
<style>
    /* 卡片样式 */
    .data-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* 卡片标题 */
    .card-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1E3A8A;
    }
    
    /* 卡片头部 */
    .card-header {
        margin-bottom: 1rem;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 0.5rem;
    }
    
    /* 统计卡片 */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 100%;
    }
    
    /* 统计数字 */
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    /* 统计标题 */
    .stat-title {
        font-size: 0.9rem;
        color: #6B7280;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    /* 统计数值 */
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1F2937;
        margin: 0.5rem 0;
    }
    
    /* 统计趋势 */
    .stat-trend {
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* 上升趋势 */
    .trend-up {
        color: #10B981;
    }
    
    /* 下降趋势 */
    .trend-down {
        color: #EF4444;
    }
    
    /* 统计增长 */
    .stat-growth {
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* 正增长 */
    .positive {
        color: #4ade80;
    }
    
    /* 负增长 */
    .negative {
        color: #f87171;
    }
    
    /* 部分标题 */
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        color: #1E3A8A;
    }
    
    /* 洞察卡片 */
    .insight-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* 洞察标题 */
    .insight-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 0.8rem;
    }
    
    /* 洞察内容 */
    .insight-content {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #495057;
    }
</style>
""", unsafe_allow_html=True)

# 管理员凭据 - 硬编码（实际应用中应该存储在数据库中并加密）
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"  # admin123的SHA-256哈希值

def admin_login():
    """管理员登录界面"""
    # 页面布局
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        # 标题区域
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2.5rem; border-radius: 16px; margin: 2rem 0; 
                    color: white; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);'>
            <h1 style='margin: 0; font-size: 2.5rem; font-weight: 700;'>👨‍💼 医脉通管理后台</h1>
            <p style='margin: 1rem 0 0 0; opacity: 0.9; font-size: 1.1rem;'>系统管理与数据分析中心</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 登录卡片
        st.markdown("""
        <div style='background-color: white; border-radius: 10px; padding: 2rem; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
            <h2 style='margin-top: 0; color: #1E3A8A; font-size: 1.5rem;'>管理员登录</h2>
            <p style='color: #6B7280; margin-bottom: 1.5rem;'>请输入您的管理员凭据以访问后台</p>
        """, unsafe_allow_html=True)
        
        # 登录表单
        with st.form("admin_login_form"):
            username = st.text_input("用户名", placeholder="请输入管理员用户名")
            password = st.text_input("密码", type="password", placeholder="请输入管理员密码")
            submit = st.form_submit_button("登录", use_container_width=True)
            
            if submit:
                if username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.rerun()
                else:
                    st.error("用户名或密码错误，请重试")
        
        st.markdown("</div>", unsafe_allow_html=True)

def admin_dashboard():
    """管理员仪表板"""
    user_manager = UserManager()
    
    # 页面标题和顶部导航栏
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 1.5rem; color: white;'>
            <h1 style='margin: 0; font-size: 2rem;'>📊 医脉通管理仪表板</h1>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>欢迎回来，{} | 当前时间：{}</p>
        </div>
        """.format(
            st.session_state.admin_username,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 退出登录", use_container_width=True, type="primary"):
            st.session_state.admin_logged_in = False
            st.session_state.admin_username = None
            st.rerun()
    
    # 时间范围选择器
    time_range_options = {
        "今日": 1,
        "近7天": 7,
        "近30天": 30,
        "近90天": 90
    }
    
    time_col1, time_col2 = st.columns([3, 1])
    with time_col1:
        time_range = st.select_slider(
            "📅 选择时间范围",
            options=list(time_range_options.keys()),
            value="近7天"
        )
    with time_col2:
        refresh_btn = st.button("🔄 刷新数据", use_container_width=True)
    
    # 获取统计数据
    stats = user_manager.get_admin_statistics()
    
    # 关键指标卡片 - 使用现代化卡片设计
    st.markdown("<div class='section-title'>📈 关键业务指标</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # 计算环比增长率（模拟数据，实际应从数据库获取）
    prev_users = stats['total_users'] * 0.9  # 假设上期用户数为当前的90%
    user_growth = (stats['total_users'] - prev_users) / prev_users * 100 if prev_users > 0 else 0
    
    prev_premium = stats['premium_users'] * 0.85  # 假设上期付费用户为当前的85%
    premium_growth = (stats['premium_users'] - prev_premium) / prev_premium * 100 if prev_premium > 0 else 0
    
    prev_active = stats['today_active'] * 0.95  # 假设上期活跃用户为当前的95%
    active_growth = (stats['today_active'] - prev_active) / prev_active * 100 if prev_active > 0 else 0
    
    prev_revenue = stats['total_revenue'] * 0.88  # 假设上期收入为当前的88%
    revenue_growth = (stats['total_revenue'] - prev_revenue) / prev_revenue * 100 if prev_revenue > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%); border-left: 4px solid #4facfe;">
            <div class="stat-title">总用户数</div>
            <div class="stat-value">{stats['total_users']}</div>
            <div class="stat-trend {'trend-up' if user_growth > 0 else 'trend-down'}">环比 {'+' if user_growth > 0 else ''}{user_growth:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(67, 233, 123, 0.1) 0%, rgba(56, 249, 215, 0.1) 100%); border-left: 4px solid #43e97b;">
            <div class="stat-title">付费用户</div>
            <div class="stat-value">{stats['premium_users']}</div>
            <div class="stat-trend {'trend-up' if premium_growth > 0 else 'trend-down'}">环比 {'+' if premium_growth > 0 else ''}{premium_growth:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(250, 112, 154, 0.1) 0%, rgba(254, 225, 64, 0.1) 100%); border-left: 4px solid #fa709a;">
            <div class="stat-title">今日活跃</div>
            <div class="stat-value">{stats['today_active']}</div>
            <div class="stat-trend {'trend-up' if active_growth > 0 else 'trend-down'}">环比 {'+' if active_growth > 0 else ''}{active_growth:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(168, 237, 234, 0.1) 0%, rgba(254, 214, 227, 0.1) 100%); border-left: 4px solid #a8edea;">
            <div class="stat-title">总收入</div>
            <div class="stat-value">¥{stats['total_revenue']:.0f}</div>
            <div class="stat-trend {'trend-up' if revenue_growth > 0 else 'trend-down'}">环比 {'+' if revenue_growth > 0 else ''}{revenue_growth:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 数据洞察卡片
    premium_ratio = stats['premium_users']/stats['total_users']*100 if stats['total_users'] > 0 else 0
    active_ratio = stats['today_active']/stats['total_users']*100 if stats['total_users'] > 0 else 0
    
    st.markdown(f"""<div class='insight-card'>
        <div class='insight-title'>📊 数据洞察</div>
        <div class='insight-content'>
            付费用户占比 <b>{premium_ratio:.1f}%</b>，活跃用户转化率 <b>{active_ratio:.1f}%</b>。建议关注用户活跃度和付费转化环节，优化用户体验提升留存率。
        </div>
    </div>""", unsafe_allow_html=True)
    
    # 使用选项卡组织不同的数据分析部分
    tabs = st.tabs(["📊 数据概览", "👥 用户管理", "💰 付费分析", "📈 使用情况", "💳 付费记录"])
    
    # 选项卡1：数据概览
    with tabs[0]:
        # 用户增长和付费转化
        st.markdown("<div class='section-title'>📊 用户增长与付费转化</div>", unsafe_allow_html=True)
        
        overview_col1, overview_col2 = st.columns(2)
        
        with overview_col1:
            # 用户类型分布饼图
            st.markdown("""<div class='data-card'>
                <div class='card-header'>
                    <div class='card-title'>用户类型分布</div>
                </div>
                <div class='card-body'>""", unsafe_allow_html=True)
            
            if 'user_type_stats' in stats:
                # 计算百分比
                total = sum(stats['user_type_stats'].values())
                percentages = {k: (v/total*100) for k, v in stats['user_type_stats'].items()} if total > 0 else {}
                
                # 创建饼图
                fig_pie = px.pie(
                    values=list(stats['user_type_stats'].values()),
                    names=list(stats['user_type_stats'].keys()),
                    color_discrete_map={
                        'free': '#ff9999',
                        'premium': '#66b3ff',
                        'enterprise': '#99ff99'
                    },
                    hole=0.4
                )
                
                # 添加注释
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=30, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # 添加数据洞察
                premium_percent = percentages.get('premium', 0) + percentages.get('enterprise', 0)
                # 根据付费比例确定提示文本
                insight_text = "付费转化率良好，可进一步提升企业版占比。" if premium_percent > 20 else "付费转化有提升空间，建议优化付费引导流程。"
                
                st.markdown(f"""<div class='insight-card' style='margin-top: 1rem;'>
                    <div class='insight-content'>
                        付费用户占比 <b>{premium_percent:.1f}%</b>，其中企业版用户 <b>{percentages.get('enterprise', 0):.1f}%</b>。
                        {insight_text}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("暂无用户类型数据")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with overview_col2:
            # 收入趋势
            st.markdown("""<div class='data-card'>
                <div class='card-header'>
                    <div class='card-title'>收入趋势分析</div>
                </div>
                <div class='card-body'>""", unsafe_allow_html=True)
            
            revenue_data = user_manager.get_revenue_trend()
            if revenue_data:
                df_revenue = pd.DataFrame(revenue_data)
                
                # 计算总收入和平均日收入
                total_period_revenue = df_revenue['revenue'].sum()
                avg_daily_revenue = df_revenue['revenue'].mean()
                
                # 创建收入趋势图
                fig_line = px.line(
                    df_revenue, 
                    x='date', 
                    y='revenue',
                    markers=True,
                    color_discrete_sequence=['#667eea']
                )
                
                fig_line.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=30, b=30),
                    xaxis_title="",
                    yaxis_title="收入(元)",
                    hovermode="x unified"
                )
                
                # 添加移动平均线
                df_revenue['ma7'] = df_revenue['revenue'].rolling(window=7, min_periods=1).mean()
                fig_line.add_scatter(x=df_revenue['date'], y=df_revenue['ma7'], mode='lines', name='7日移动平均', line=dict(color='#ff9999', width=2, dash='dot'))
                
                st.plotly_chart(fig_line, use_container_width=True)
                
                # 添加数据洞察
                recent_trend = "上升" if df_revenue['revenue'].iloc[-3:].mean() > df_revenue['revenue'].iloc[-6:-3].mean() else "下降"
                # 根据收入趋势确定提示文本
                trend_advice = "建议分析高收入日期的营销活动效果。" if recent_trend == "上升" else "建议加强用户促活和付费转化。"
                
                st.markdown(f"""<div class='insight-card' style='margin-top: 1rem;'>
                    <div class='insight-content'>
                        期内总收入 <b>¥{total_period_revenue:.0f}</b>，日均收入 <b>¥{avg_daily_revenue:.0f}</b>。
                        近期收入呈<b>{recent_trend}</b>趋势，{trend_advice}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("暂无收入数据")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # 使用情况概览
        st.markdown("<div class='section-title'>📱 使用情况概览</div>", unsafe_allow_html=True)
        
        usage_col1, usage_col2 = st.columns(2)
        
        with usage_col1:
            # 每日使用量趋势
            st.markdown("""<div class='data-card'>
                <div class='card-header'>
                    <div class='card-title'>每日使用量趋势</div>
                </div>
                <div class='card-body'>""", unsafe_allow_html=True)
            
            usage_data = user_manager.get_usage_trend()
            if usage_data:
                df_usage = pd.DataFrame(usage_data)
                
                # 计算总使用量和平均日使用量
                total_usage = df_usage['usage_count'].sum()
                avg_daily_usage = df_usage['usage_count'].mean()
                
                # 创建使用量趋势图
                fig_usage = px.bar(
                    df_usage,
                    x='date',
                    y='usage_count',
                    color_discrete_sequence=['#4facfe']
                )
                
                # 添加趋势线
                fig_usage.add_scatter(
                    x=df_usage['date'], 
                    y=df_usage['usage_count'], 
                    mode='lines', 
                    name='趋势',
                    line=dict(color='#ff6b6b', width=2)
                )
                
                fig_usage.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=30, b=30),
                    xaxis_title="",
                    yaxis_title="使用次数",
                    showlegend=False,
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig_usage, use_container_width=True)
                
                # 添加数据洞察
                peak_day = df_usage.loc[df_usage['usage_count'].idxmax()]
                # 使用量洞察提示
                usage_insight = "周末使用量明显下降，建议开发更多休闲场景功能。"
                
                st.markdown(f"""<div class='insight-card' style='margin-top: 1rem;'>
                    <div class='insight-content'>
                        期内总使用量 <b>{total_usage}</b> 次，日均 <b>{avg_daily_usage:.0f}</b> 次。
                        峰值出现在 <b>{peak_day['date']}</b>，使用量 <b>{peak_day['usage_count']}</b> 次。
                        {usage_insight}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("暂无使用数据")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with usage_col2:
            # 科室使用分布
            st.markdown("""<div class='data-card'>
                <div class='card-header'>
                    <div class='card-title'>科室使用分布</div>
                </div>
                <div class='card-body'>""", unsafe_allow_html=True)
            
            dept_data = user_manager.get_department_usage()
            if dept_data:
                df_dept = pd.DataFrame(dept_data)
                
                # 按使用量排序
                df_dept = df_dept.sort_values('usage_count', ascending=False)
                
                # 创建科室使用分布图
                fig_dept = px.bar(
                    df_dept,
                    x='department',
                    y='usage_count',
                    color='usage_count',
                    color_continuous_scale='Viridis',
                    text='usage_count'
                )
                
                fig_dept.update_traces(texttemplate='%{text}', textposition='outside')
                fig_dept.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=30, b=80),
                    xaxis_title="",
                    yaxis_title="使用次数",
                    coloraxis_showscale=False,
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig_dept, use_container_width=True)
                
                # 添加数据洞察
                top_dept = df_dept.iloc[0]['department']
                top_usage = df_dept.iloc[0]['usage_count']
                total_usage = df_dept['usage_count'].sum()
                st.markdown(f"""<div class='insight-card' style='margin-top: 1rem;'>
                    <div class='insight-content'>
                        <b>{top_dept}</b> 科室使用量最高，占比 <b>{top_usage/total_usage*100:.1f}%</b>。
                        建议针对高使用量科室开发专业化功能，对低使用量科室进行针对性推广。
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("暂无科室使用数据")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    # 选项卡2：用户管理
    with tabs[1]:
        st.markdown("<div class='section-title'>👥 用户管理</div>", unsafe_allow_html=True)
        
        # 获取所有用户信息
        all_users = user_manager.get_all_users_info()
        
        if all_users:
            # 用户筛选和搜索
            filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])
            
            with filter_col1:
                user_type_filter = st.selectbox(
                    "用户类型",
                    ["全部", "free", "premium", "enterprise", "admin"],
                    key="user_type_filter"
                )
            
            with filter_col2:
                user_search = st.text_input("搜索用户", placeholder="输入用户名或邮箱", key="user_search")
            
            with filter_col3:
                st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
                refresh_users = st.button("🔄 刷新", key="refresh_users")
            
            # 转换为DataFrame
            df_users = pd.DataFrame(all_users)
            
            # 应用筛选
            filtered_users = df_users.copy()
            
            if user_type_filter != "全部":
                filtered_users = filtered_users[filtered_users['user_type'] == user_type_filter]
            
            if user_search:
                filtered_users = filtered_users[
                    filtered_users['username'].str.contains(user_search, case=False, na=False) |
                    filtered_users['email'].str.contains(user_search, case=False, na=False)
                ]
            
            # 显示筛选结果统计
            st.markdown(f"<p>找到 <b>{len(filtered_users)}</b> 个用户 (共 {len(df_users)} 个)</p>", unsafe_allow_html=True)
            
            # 用户管理功能
            user_mgmt_col1, user_mgmt_col2 = st.columns([3, 1])
            
            with user_mgmt_col1:
                # 用户表格
                st.dataframe(
                    filtered_users,
                    use_container_width=True,
                    column_config={
                        "id": st.column_config.TextColumn("用户ID", width="small"),
                        "username": st.column_config.TextColumn("用户名", width="medium"),
                        "email": st.column_config.TextColumn("邮箱", width="medium"),
                        "user_type": st.column_config.SelectboxColumn(
                            "用户类型",
                            width="small",
                            options=["free", "premium", "enterprise", "admin"]
                        ),
                        "created_at": st.column_config.DatetimeColumn(
                            "注册时间",
                            format="YYYY-MM-DD HH:mm",
                            width="medium"
                        ),
                        "last_login": st.column_config.DatetimeColumn(
                            "最后登录",
                            format="YYYY-MM-DD HH:mm",
                            width="medium"
                        ),
                        "total_usage": st.column_config.NumberColumn(
                            "总使用次数",
                            width="small"
                        ),
                        "today_usage": st.column_config.NumberColumn(
                            "今日使用",
                            width="small"
                        ),
                        "daily_limit": st.column_config.NumberColumn(
                            "每日限额",
                            width="small"
                        ),
                        "remaining_usage": st.column_config.NumberColumn(
                            "剩余次数",
                            width="small"
                        )
                    },
                    height=400
                )
            
            with user_mgmt_col2:
                # 用户管理操作
                st.markdown("<div class='data-card'>", unsafe_allow_html=True)
                st.markdown("<h4>用户操作</h4>", unsafe_allow_html=True)
                
                # 设置管理员权限
                st.markdown("<h5>设置管理员</h5>", unsafe_allow_html=True)
                with st.form("set_admin_form"):
                    admin_username = st.text_input("用户名", placeholder="输入要设置为管理员的用户名")
                    set_admin_submit = st.form_submit_button("设置为管理员", type="primary")
                    
                    if set_admin_submit and admin_username:
                        success, message = user_manager.set_user_as_admin(admin_username)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                
                # 其他用户管理功能可以在这里添加
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("暂无用户数据")
    
    # 选项卡3：付费分析
    with tabs[2]:
        st.markdown("<div class='section-title'>💰 付费分析</div>", unsafe_allow_html=True)
        
        # 付费概览
        pay_col1, pay_col2 = st.columns(2)
        
        with pay_col1:
            # 用户类型分布
            st.markdown("""<div class='data-card'>
                <div class='card-header'>
                    <div class='card-title'>用户类型分布</div>
                </div>
                <div class='card-body'>""", unsafe_allow_html=True)
            
            if 'user_type_stats' in stats:
                # 创建饼图
                fig_pie = px.pie(
                    values=list(stats['user_type_stats'].values()),
                    names=list(stats['user_type_stats'].keys()),
                    color_discrete_map={
                        'free': '#ff9999',
                        'premium': '#66b3ff',
                        'enterprise': '#99ff99'
                    },
                    hole=0.4
                )
                
                # 添加注释
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=30, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    annotations=[dict(text='用户类型', x=0.5, y=0.5, font_size=15, showarrow=False)]
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("暂无用户类型数据")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with pay_col2:
            # 收入趋势
            st.markdown("""<div class='data-card'>
                <div class='card-header'>
                    <div class='card-title'>收入趋势</div>
                </div>
                <div class='card-body'>""", unsafe_allow_html=True)
            
            revenue_data = user_manager.get_revenue_trend()
            if revenue_data:
                df_revenue = pd.DataFrame(revenue_data)
                
                # 创建收入趋势图
                fig_line = px.line(
                    df_revenue, 
                    x='date', 
                    y='revenue',
                    markers=True,
                    color_discrete_sequence=['#667eea']
                )
                
                fig_line.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=30, b=30),
                    xaxis_title="",
                    yaxis_title="收入(元)"
                )
                
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("暂无收入数据")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    # 选项卡4：使用情况分析
    with tabs[3]:
        st.markdown("<div class='section-title'>📊 使用情况分析</div>", unsafe_allow_html=True)
        
        # 时间范围选择
        usage_date_col1, usage_date_col2 = st.columns([3, 1])
        with usage_date_col1:
            usage_date_range = st.select_slider(
                "选择分析时间范围",
                options=["近7天", "近30天", "近90天", "全部时间"],
                value="近7天"
            )
        with usage_date_col2:
            st.button("刷新数据", key="refresh_usage_data", use_container_width=True)
        
        # 使用趋势分析
        st.markdown("""<div class='data-card'>
            <div class='card-header'>
                <div class='card-title'>使用趋势分析</div>
            </div>
            <div class='card-body'>""", unsafe_allow_html=True)
        
        usage_trend_col1, usage_trend_col2 = st.columns([3, 1])
        
        with usage_trend_col1:
            # 每日使用量趋势
            usage_data = user_manager.get_usage_trend()
            if usage_data:
                df_usage = pd.DataFrame(usage_data)
                
                # 创建使用量趋势图
                fig_usage = px.bar(
                    df_usage,
                    x='date',
                    y='usage_count',
                    color_discrete_sequence=['#4facfe']
                )
                
                # 添加趋势线
                fig_usage.add_scatter(
                    x=df_usage['date'], 
                    y=df_usage['usage_count'], 
                    mode='lines', 
                    name='趋势',
                    line=dict(color='#ff6b6b', width=2)
                )
                
                fig_usage.update_layout(
                    height=350,
                    margin=dict(l=20, r=20, t=30, b=30),
                    xaxis_title="",
                    yaxis_title="使用次数",
                    showlegend=False,
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig_usage, use_container_width=True)
            else:
                st.info("暂无使用数据")
        
        with usage_trend_col2:
            if usage_data:
                df_usage = pd.DataFrame(usage_data)
                
                # 计算统计数据
                total_usage = df_usage['usage_count'].sum()
                avg_daily_usage = df_usage['usage_count'].mean()
                max_usage = df_usage['usage_count'].max()
                max_date = df_usage.loc[df_usage['usage_count'].idxmax(), 'date']
                
                # 显示统计数据
                st.metric("总使用量", f"{total_usage} 次")
                st.metric("日均使用量", f"{avg_daily_usage:.1f} 次")
                st.metric("峰值使用量", f"{max_usage} 次", f"({max_date})")
                
                # 计算环比增长
                if len(df_usage) >= 2:
                    current = df_usage['usage_count'].iloc[-1]
                    previous = df_usage['usage_count'].iloc[-2]
                    growth_rate = (current - previous) / previous * 100 if previous > 0 else 0
                    st.metric(
                        "环比增长", 
                        f"{growth_rate:+.1f}%", 
                        delta_color="normal" if growth_rate >= 0 else "inverse"
                    )
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # 使用分布分析
        usage_dist_col1, usage_dist_col2 = st.columns(2)
        
        with usage_dist_col1:
            # 科室使用分布
            st.markdown("""<div class='data-card'>
                <div class='card-header'>
                    <div class='card-title'>科室使用分布</div>
                </div>
                <div class='card-body'>""", unsafe_allow_html=True)
            
            dept_data = user_manager.get_department_usage()
            if dept_data:
                df_dept = pd.DataFrame(dept_data)
                
                # 按使用量排序
                df_dept = df_dept.sort_values('usage_count', ascending=False)
                
                # 创建科室使用分布图
                fig_dept = px.bar(
                    df_dept,
                    x='department',
                    y='usage_count',
                    color='usage_count',
                    color_continuous_scale='Viridis',
                    text='usage_count'
                )
                
                fig_dept.update_traces(texttemplate='%{text}', textposition='outside')
                fig_dept.update_layout(
                    height=350,
                    margin=dict(l=20, r=20, t=30, b=80),
                    xaxis_title="",
                    yaxis_title="使用次数",
                    coloraxis_showscale=False,
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig_dept, use_container_width=True)
                
                # 添加数据洞察
                top_dept = df_dept.iloc[0]['department']
                top_usage = df_dept.iloc[0]['usage_count']
                total_usage = df_dept['usage_count'].sum()
                st.markdown(f"""<div class='insight-card'>
                    <div class='insight-content'>
                        <b>{top_dept}</b> 科室使用量最高，占比 <b>{top_usage/total_usage*100:.1f}%</b>。
                        建议针对高使用量科室开发专业化功能，对低使用量科室进行针对性推广。
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("暂无科室使用数据")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with usage_dist_col2:
            # 用户类型使用分布（模拟数据）
            st.markdown("""<div class='data-card'>
                <div class='card-header'>
                    <div class='card-title'>用户类型使用分布</div>
                </div>
                <div class='card-body'>""", unsafe_allow_html=True)
            
            # 模拟数据 - 实际应从数据库获取
            user_usage_data = [
                {"user_type": "free", "usage_count": 120},
                {"user_type": "premium", "usage_count": 350},
                {"user_type": "enterprise", "usage_count": 530}
            ]
            
            df_user_usage = pd.DataFrame(user_usage_data)
            
            # 创建用户类型使用分布图
            fig_user_usage = px.pie(
                df_user_usage,
                values='usage_count',
                names='user_type',
                color='user_type',
                color_discrete_map={
                    'free': '#ff9999',
                    'premium': '#66b3ff',
                    'enterprise': '#99ff99'
                },
                hole=0.4
            )
            
            fig_user_usage.update_traces(textposition='inside', textinfo='percent+label')
            fig_user_usage.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=30, b=30),
                annotations=[dict(text='使用分布', x=0.5, y=0.5, font_size=15, showarrow=False)]
            )
            
            st.plotly_chart(fig_user_usage, use_container_width=True)
            
            # 添加数据洞察
            total_usage = sum(item['usage_count'] for item in user_usage_data)
            premium_usage = user_usage_data[1]['usage_count'] + user_usage_data[2]['usage_count']
            premium_ratio = premium_usage / total_usage * 100 if total_usage > 0 else 0
            
            st.markdown(f"""<div class='insight-card'>
                <div class='insight-content'>
                    付费用户使用占比 <b>{premium_ratio:.1f}%</b>，高于用户数量占比，
                    表明付费用户活跃度更高，建议进一步提升免费用户转化率。
                </div>
            </div>""", unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    # 选项卡5：付费记录
    with tabs[4]:
        st.markdown("<div class='section-title'>💳 付费记录</div>", unsafe_allow_html=True)
        
        # 付费记录筛选
        st.markdown("""<div class='data-card'>
            <div class='card-header'>
                <div class='card-title'>付费记录筛选</div>
            </div>
            <div class='card-body'>""", unsafe_allow_html=True)
        
        payment_filter_col1, payment_filter_col2, payment_filter_col3 = st.columns(3)
        
        with payment_filter_col1:
            payment_status_filter = st.selectbox(
                "支付状态",
                ["全部", "success", "pending", "failed"],
                format_func=lambda x: {
                    "全部": "全部状态",
                    "success": "支付成功",
                    "pending": "处理中",
                    "failed": "支付失败"
                }.get(x, x)
            )
        
        with payment_filter_col2:
            payment_type_filter = st.selectbox(
                "套餐类型",
                ["全部", "premium", "enterprise"],
                format_func=lambda x: {
                    "全部": "全部套餐",
                    "premium": "高级套餐",
                    "enterprise": "企业套餐"
                }.get(x, x)
            )
        
        with payment_filter_col3:
            payment_search = st.text_input("搜索用户", placeholder="输入用户名")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # 付费记录表格
        st.markdown("""<div class='data-card'>
            <div class='card-header'>
                <div class='card-title'>付费记录列表</div>
            </div>
            <div class='card-body' style='padding: 0.5rem;'>""", unsafe_allow_html=True)
        
        payment_records = user_manager.get_payment_records()
        
        if payment_records:
            df_payments = pd.DataFrame(payment_records)
            
            # 应用筛选
            filtered_payments = df_payments.copy()
            
            if payment_status_filter != "全部":
                filtered_payments = filtered_payments[filtered_payments['payment_status'] == payment_status_filter]
            
            if payment_type_filter != "全部":
                filtered_payments = filtered_payments[filtered_payments['plan_type'] == payment_type_filter]
            
            if payment_search:
                filtered_payments = filtered_payments[
                    filtered_payments['username'].str.contains(payment_search, case=False, na=False)
                ]
            
            # 显示筛选结果统计
            st.markdown(f"<p>找到 <b>{len(filtered_payments)}</b> 条付费记录 (共 {len(df_payments)} 条)</p>", unsafe_allow_html=True)
            
            # 显示付费记录表格
            st.dataframe(
                filtered_payments,
                use_container_width=True,
                column_config={
                    "id": st.column_config.TextColumn("记录ID", width="small"),
                    "username": st.column_config.TextColumn("用户名", width="medium"),
                    "plan_type": st.column_config.SelectboxColumn(
                        "套餐类型",
                        width="medium",
                        options=["premium", "enterprise"]
                    ),
                    "amount": st.column_config.NumberColumn(
                        "金额",
                        format="¥%.2f",
                        width="small"
                    ),
                    "payment_method": st.column_config.SelectboxColumn(
                        "支付方式",
                        width="small",
                        options=["alipay", "wechat", "bank"]
                    ),
                    "payment_status": st.column_config.SelectboxColumn(
                        "支付状态",
                        width="small",
                        options=["success", "pending", "failed"]
                    ),
                    "start_date": st.column_config.DatetimeColumn(
                        "开始时间",
                        format="YYYY-MM-DD",
                        width="medium"
                    ),
                    "end_date": st.column_config.DatetimeColumn(
                        "结束时间",
                        format="YYYY-MM-DD",
                        width="medium"
                    ),
                    "created_at": st.column_config.DatetimeColumn(
                        "创建时间",
                        format="YYYY-MM-DD HH:mm",
                        width="medium"
                    )
                },
                height=400
            )
        else:
            st.info("暂无付费记录")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # 付费统计分析
        st.markdown("""<div class='data-card'>
            <div class='card-header'>
                <div class='card-title'>付费统计分析</div>
            </div>
            <div class='card-body'>""", unsafe_allow_html=True)
        
        if payment_records:
            df_payments = pd.DataFrame(payment_records)
            
            payment_stat_col1, payment_stat_col2, payment_stat_col3 = st.columns(3)
            
            with payment_stat_col1:
                # 总收入
                total_revenue = df_payments['amount'].sum()
                st.metric(
                    "总收入", 
                    f"¥{total_revenue:.2f}"
                )
            
            with payment_stat_col2:
                # 平均订单金额
                avg_order = df_payments['amount'].mean() if len(df_payments) > 0 else 0
                st.metric(
                    "平均订单金额", 
                    f"¥{avg_order:.2f}"
                )
            
            with payment_stat_col3:
                # 成功率
                success_count = len(df_payments[df_payments['payment_status'] == 'success'])
                success_rate = success_count / len(df_payments) * 100 if len(df_payments) > 0 else 0
                st.metric(
                    "支付成功率", 
                    f"{success_rate:.1f}%"
                )
        else:
            st.info("暂无付费统计数据")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

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