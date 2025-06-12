import streamlit as st
from datetime import datetime, timedelta
from utils.user_manager import UserManager

class SessionManager:
    """统一的会话管理器，确保登录状态在所有页面间保持一致"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.auto_login_duration = 3  # 3分钟自动登录
        self._init_session_state()
    
    def _init_session_state(self):
        """初始化session state"""
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'user_info' not in st.session_state:
            st.session_state.user_info = None
        if 'show_register' not in st.session_state:
            st.session_state.show_register = False
        if 'auto_login_info' not in st.session_state:
            st.session_state.auto_login_info = None
    
    def save_login_state(self, user_info):
        """保存登录状态"""
        st.session_state.logged_in = True
        st.session_state.user_info = user_info
        
        # 保存自动登录信息
        st.session_state.auto_login_info = {
            'session_id': user_info['session_id'],
            'login_time': datetime.now().isoformat(),
            'user_info': user_info
        }
    
    def check_auto_login(self):
        """检查自动登录状态"""
        if (st.session_state.auto_login_info is None or 
            not isinstance(st.session_state.auto_login_info, dict)):
            return False, None
        
        auto_login_info = st.session_state.auto_login_info
        
        # 检查必要的字段是否存在
        if 'login_time' not in auto_login_info or 'session_id' not in auto_login_info:
            self.clear_login_state()
            return False, None
        
        try:
            login_time = datetime.fromisoformat(auto_login_info['login_time'])
        except (ValueError, TypeError):
            self.clear_login_state()
            return False, None
        
        # 检查是否在自动登录时间内
        if datetime.now() - login_time < timedelta(minutes=self.auto_login_duration):
            # 验证session是否仍然有效
            valid, user_info = self.user_manager.validate_session(auto_login_info['session_id'])
            if valid:
                # 更新session state
                st.session_state.logged_in = True
                st.session_state.user_info = user_info
                return True, user_info
            else:
                # session无效，清除自动登录信息
                self.clear_login_state()
        else:
            # 超时，清除自动登录信息
            self.clear_login_state()
        
        return False, None
    
    def clear_login_state(self):
        """清除登录状态"""
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.auto_login_info = None
    
    def is_logged_in(self):
        """检查是否已登录"""
        # 首先检查自动登录
        auto_logged_in, user_info = self.check_auto_login()
        if auto_logged_in:
            return True, user_info
        
        # 检查常规登录状态
        if st.session_state.logged_in and st.session_state.user_info:
            return True, st.session_state.user_info
        
        return False, None
    
    def get_remaining_time(self):
        """获取剩余自动登录时间（分钟）"""
        if (st.session_state.auto_login_info is None or 
            not isinstance(st.session_state.auto_login_info, dict)):
            return 0
        
        auto_login_info = st.session_state.auto_login_info
        
        # 检查必要的字段是否存在
        if 'login_time' not in auto_login_info:
            return 0
        
        try:
            login_time = datetime.fromisoformat(auto_login_info['login_time'])
            elapsed = (datetime.now() - login_time).total_seconds() / 60
            remaining = max(0, self.auto_login_duration - elapsed)
            return int(remaining)
        except (ValueError, TypeError):
            return 0
    
    def login(self, username, password):
        """用户登录"""
        success, result = self.user_manager.login_user(username, password)
        if success:
            self.save_login_state(result)
            return True, result
        return False, result
    
    def logout(self):
        """用户登出"""
        if st.session_state.user_info and 'session_id' in st.session_state.user_info:
            self.user_manager.logout_user(st.session_state.user_info['session_id'])
        
        self.clear_login_state()
        return True, "登出成功"