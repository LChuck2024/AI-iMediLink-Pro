import streamlit as st
import re
from utils.user_manager import UserManager
from datetime import datetime, timedelta

class AuthUI:
    def __init__(self, session_manager=None):
        self.user_manager = UserManager()
        self.session_manager = session_manager
        
    def validate_email(self, email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        """验证密码强度"""
        if len(password) < 6:
            return False, "密码长度至少6位"
        if not re.search(r'[A-Za-z]', password):
            return False, "密码必须包含字母"
        if not re.search(r'\d', password):
            return False, "密码必须包含数字"
        return True, "密码格式正确"
    
    def show_login_form(self):
        
        """显示登录表单"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 2rem;'>🔐 用户登录</h3>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>登录后享受更多专业服务
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col2:
                username = st.text_input("👤 用户名", placeholder="请输入用户名")
                password = st.text_input("🔒 密码", type="password", placeholder="请输入密码")
                
                col_login, col_register, col_guest = st.columns(3)
                
                with col_login:
                    login_clicked = st.form_submit_button("🚀 登录", use_container_width=True)
                
                with col_register:
                    register_clicked = st.form_submit_button("📝 注册新账户", use_container_width=True)

                with col_guest:
                    guest_clicked = st.form_submit_button("🎭 游客体验", use_container_width=True)

        # 添加调试信息
        if login_clicked:
            # st.write("登录按钮被点击")
            if username and password:
                # st.write(f"尝试登录用户: {username}")
                if self.session_manager:
                    try:
                        success, result = self.session_manager.login(username, password)
                        # st.write(f"登录结果: {success}, {result}")
                    except Exception as e:
                        st.error(f"登录过程中发生错误: {str(e)}")
                else:
                    try:
                        success, result = self.user_manager.login_user(username, password)
                        st.write(f"直接登录结果: {success}, {result}")
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_info = result
                    except Exception as e:
                        st.error(f"直接登录过程中发生错误: {str(e)}")
                
                if success:
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.error("请输入用户名和密码")
        
        if register_clicked:
            st.session_state.show_register = True
            st.rerun()
        
        if guest_clicked:
            st.switch_page("pages/1_医脉通.py")
    
    def show_register_form(self):
        """显示注册表单"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white; text-align: center;'>
            <h3 style='margin: 0; font-size: 2rem;'>📝 用户注册</h3>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>创建账户，开启智能医疗之旅</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("register_form"):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                username = st.text_input("👤 用户名", placeholder="请输入用户名（3-20位字符）")
                email = st.text_input("📧 邮箱", placeholder="请输入邮箱地址")
                password = st.text_input("🔒 密码", type="password", placeholder="请输入密码（至少6位，包含字母和数字）")
                confirm_password = st.text_input("🔒 确认密码", type="password", placeholder="请再次输入密码")
                
                # 服务条款
                agree_terms = st.checkbox("我已阅读并同意《服务条款》和《隐私政策》")
                
                col_register, col_back = st.columns(2)
                
                with col_register:
                    register_clicked = st.form_submit_button("🎉 立即注册", use_container_width=True)
                
                with col_back:
                    back_clicked = st.form_submit_button("🔙 返回登录", use_container_width=True)
        
        if register_clicked:
            # 验证输入
            if not all([username, email, password, confirm_password]):
                st.error("❌ 请填写完整的注册信息")
            elif len(username) < 3 or len(username) > 20:
                st.error("❌ 用户名长度应在3-20位之间")
            elif not self.validate_email(email):
                st.error("❌ 请输入有效的邮箱地址")
            elif password != confirm_password:
                st.error("❌ 两次输入的密码不一致")
            else:
                valid_password, password_msg = self.validate_password(password)
                if not valid_password:
                    st.error(f"❌ {password_msg}")
                elif not agree_terms:
                    st.error("❌ 请同意服务条款和隐私政策")
                else:
                    # 执行注册
                    success, message = self.user_manager.register_user(username, email, password)
                    if success:
                        st.success("🎉 注册成功！请登录您的账户")
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        if back_clicked:
            st.session_state.show_register = False
            st.rerun()
    
    def show_user_info(self, user_info):
        """显示用户信息"""
        # 获取用户统计信息
        stats = self.user_manager.get_user_stats(user_info['user_id'])
        
        # 检查使用限制
        can_use, daily_count, limit = self.user_manager.check_usage_limit(
            user_info['user_id'], user_info['user_type']
        )
        
        # 用户类型显示
        user_type_display = {
            'free': '🆓 免费用户',
            'premium': '💎 高级用户', 
            'enterprise': '🏢 企业用户'
        }
        
        # 用户信息卡片
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; color: white;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h3 style='margin: 0; font-size: 1.3rem;'>👋 欢迎，{user_info['username']}</h3>
                    <p style='margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.9rem;'>{user_type_display.get(user_info['user_type'], '🆓 免费用户')}</p>
                </div>
                <div style='text-align: right;'>
                    <p style='margin: 0; font-size: 0.8rem; opacity: 0.8;'>今日咨询</p>
                    <p style='margin: 0; font-size: 1.2rem; font-weight: bold;'>{daily_count}/{limit}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 使用统计
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 总咨询次数", stats['total_usage'])
        
        with col2:
            st.metric("📅 今日咨询", f"{daily_count}/{limit}")
        
        with col3:
            remaining = limit - daily_count
            st.metric("⏳ 剩余次数", remaining if remaining > 0 else 0)
        
        with col4:
            favorite = stats['favorite_department'] or "暂无"
            st.metric("❤️ 常用科室", favorite)
        
        # 使用限制提醒
        if not can_use:
            st.warning(f"⚠️ 您今日的咨询次数已达上限（{limit}次）。升级为高级用户可享受更多咨询次数！")
            if st.button("💎 立即升级", key="upgrade_button"):
                self.show_upgrade_options(user_info['user_id'])
        elif daily_count >= limit * 0.8:  # 使用量超过80%时提醒
            st.info(f"💡 您今日已使用 {daily_count}/{limit} 次咨询。考虑升级获得更多服务！")
        
        # 登出按钮
        if st.button("🚪 退出登录", key="logout_button"):
            self.logout()
    
    def show_upgrade_options(self, user_id):
        """显示升级选项"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); 
                    padding: 1.5rem; border-radius: 15px; margin: 1rem 0; color: #2d3436;'>
            <h3 style='margin: 0 0 1rem 0; text-align: center;'>💎 升级高级用户</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; text-align: center; 
                        border: 2px solid #ddd; margin-bottom: 1rem;'>
                <h4 style='color: #667eea; margin: 0 0 1rem 0;'>📅 月度套餐</h4>
                <p style='font-size: 2rem; font-weight: bold; color: #2d3436; margin: 0;'>¥39</p>
                <p style='color: #636e72; margin: 0.5rem 0;'>每月50次咨询</p>
                <p style='color: #636e72; margin: 0;'>专业健康报告</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("选择月度", key="monthly", use_container_width=True):
                success, message = self.user_manager.upgrade_user(user_id, 'monthly', 39.0)
                if success:
                    st.success("🎉 升级成功！")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        
        with col2:
            st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; text-align: center; 
                        border: 3px solid #667eea; margin-bottom: 1rem; position: relative;'>
                <div style='background: #667eea; color: white; padding: 0.3rem; border-radius: 15px; 
                            position: absolute; top: -10px; left: 50%; transform: translateX(-50%); 
                            font-size: 0.8rem;'>推荐</div>
                <h4 style='color: #667eea; margin: 0 0 1rem 0;'>📈 季度套餐</h4>
                <p style='font-size: 2rem; font-weight: bold; color: #2d3436; margin: 0;'>¥99</p>
                <p style='color: #636e72; margin: 0.5rem 0;'>每月50次咨询</p>
                <p style='color: #636e72; margin: 0;'>节省¥18</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("选择季度", key="quarterly", use_container_width=True):
                success, message = self.user_manager.upgrade_user(user_id, 'quarterly', 99.0)
                if success:
                    st.success("🎉 升级成功！")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        
        with col3:
            st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; text-align: center; 
                        border: 2px solid #ddd; margin-bottom: 1rem;'>
                <h4 style='color: #667eea; margin: 0 0 1rem 0;'>🎯 年度套餐</h4>
                <p style='font-size: 2rem; font-weight: bold; color: #2d3436; margin: 0;'>¥299</p>
                <p style='color: #636e72; margin: 0.5rem 0;'>每月50次咨询</p>
                <p style='color: #636e72; margin: 0;'>节省¥169</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("选择年度", key="yearly", use_container_width=True):
                success, message = self.user_manager.upgrade_user(user_id, 'yearly', 299.0)
                if success:
                    st.success("🎉 升级成功！")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    def logout(self):
        """用户登出"""
        if 'user_info' in st.session_state and 'session_id' in st.session_state.user_info:
            self.user_manager.logout_user(st.session_state.user_info['session_id'])
        
        # 清除session state
        for key in ['logged_in', 'user_info', 'show_register']:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("👋 已成功退出登录")
        st.rerun()
    
    def check_login_status(self):
        """检查登录状态"""
        if 'logged_in' in st.session_state and st.session_state.logged_in:
            if 'user_info' in st.session_state and 'session_id' in st.session_state.user_info:
                # 验证会话是否仍然有效
                valid, user_info = self.user_manager.validate_session(
                    st.session_state.user_info['session_id']
                )
                if valid:
                    # 更新用户信息
                    st.session_state.user_info.update(user_info)
                    return True, st.session_state.user_info
                else:
                    # 会话无效，清除登录状态
                    self.logout()
                    return False, None
        return False, None
    
    def check_auto_login(self):
        """检查自动登录状态（3分钟内免登录）"""
        # 检查是否有自动登录信息
        auto_login_key = 'auto_login_info'
        if auto_login_key in st.session_state and st.session_state[auto_login_key] is not None:
            auto_login_info = st.session_state[auto_login_key]
            if 'login_time' in auto_login_info and 'session_id' in auto_login_info:
                login_time = datetime.fromisoformat(auto_login_info['login_time'])
                
                # 检查是否在3分钟内
                if datetime.now() - login_time < timedelta(minutes=3):
                    # 验证session是否仍然有效
                    valid, user_info = self.user_manager.validate_session(auto_login_info['session_id'])
                    if valid:
                        # 自动登录成功
                        st.session_state.logged_in = True
                        st.session_state.user_info = user_info
                        return True, user_info
                    else:
                        # session无效，清除自动登录信息
                        del st.session_state[auto_login_key]
                else:
                    # 超过3分钟，清除自动登录信息
                    del st.session_state[auto_login_key]
            else:
                # 数据格式不正确，清除自动登录信息
                del st.session_state[auto_login_key]
        
        return False, None
    
    def save_auto_login_info(self, user_info):
        """保存自动登录信息"""
        st.session_state['auto_login_info'] = {
            'session_id': user_info['session_id'],
            'login_time': datetime.now().isoformat(),
            'user_info': user_info
        }
    
    def render_auth_interface(self):
        st.markdown("""
            <div class='cta-section'>
                <h2 style='margin-bottom: 1rem; font-size: 2rem;'>🚀 开始您的智能医疗咨询之旅</h2>
                <p style='font-size: 1.1rem; margin-bottom: 1rem; opacity: 0.9;'>专业AI助手随时为您提供医疗咨询服务，让健康管理更简单</p>
                <div style='background: rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>
                    <p style='font-size: 1rem; margin-bottom: 1rem; opacity: 0.9;'>🎭 游客模式：每日5次免费咨询</p>
                    <p style='font-size: 1rem; margin-bottom: 1rem; opacity: 0.9;'>🔐 注册登录：每日10次咨询机会</p>
                    <p style='font-size: 0.9rem; opacity: 0.8;'>登录后您将获得：个性化咨询记录、使用统计、专业建议保存等功能</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        """渲染认证界面"""
        # 首先检查自动登录
        auto_logged_in, auto_user_info = self.check_auto_login()
        if auto_logged_in:
            self.show_user_info(auto_user_info)
            return True, auto_user_info
        
        # 检查常规登录状态
        is_logged_in, user_info = self.check_login_status()
        
        if is_logged_in:
            # 已登录，显示用户信息
            self.show_user_info(user_info)
            return True, user_info
        else:
            # 未登录，显示登录/注册界面
            if st.session_state.get('show_register', False):
                self.show_register_form()
            else:
                self.show_login_form()
            return False, None
