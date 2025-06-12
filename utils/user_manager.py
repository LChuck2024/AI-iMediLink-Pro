import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
import streamlit as st
import os
from utils.db_connection_pool import SQLiteConnectionPool
from utils.logger import Logger

class UserManager:
    def __init__(self, db_path=None, max_connections=5):
        # 初始化日志记录器
        self.logger = Logger.get_instance()
        
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # 如果没有指定db_path，从配置文件读取
        if db_path is None:
            try:
                config = self.load_config()
                db_path = config.get('database', {}).get('user_db_path', 'data/users.db')
            except Exception as e:
                self.logger.error(f"从配置文件读取数据库路径失败，使用默认路径", {"error": str(e)})
                db_path = "data/users.db"
        
        self.db_path = os.path.join(project_root, db_path)
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化数据库连接池
        self.connection_pool = SQLiteConnectionPool.get_instance(self.db_path, max_connections)
        
        self.init_database()
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            # 直接使用tools.py中相同的逻辑加载完整配置
            import json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(current_dir, 'config.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载配置文件失败", {"error": str(e)})
            # 返回默认配置
            return {
                "limits": {
                    "free_daily_limit": 3,
                    "premium_daily_limit": 50,
                    "enterprise_daily_limit": 1000
                }
            }
    
    def get_user_limits(self):
        """获取用户类型限制"""
        limits_config = self.config.get('limits', {})
        return {
            'guest': limits_config.get('guest_daily_limit', 1),
            'free': limits_config.get('free_daily_limit', 5),
            'premium': limits_config.get('premium_daily_limit', 50),
            'enterprise': limits_config.get('enterprise_daily_limit', 1000)
        }
    
    def init_database(self):
        """初始化数据库表"""
        with self.connection_pool.connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    user_type TEXT DEFAULT 'free',  -- free, premium, enterprise
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # 会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # 使用记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usage_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action_type TEXT,  -- consultation, report_analysis, etc.
                    department TEXT,   -- 科室
                    tokens_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 支付记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                payment_type TEXT,  -- subscription, one-time, etc.
                payment_method TEXT,  -- credit_card, alipay, wechat, etc.
                status TEXT,  -- success, pending, failed
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 游客使用记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guest_usage_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                action_type TEXT,
                tokens_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_id(self):
        """生成会话ID"""
        return str(uuid.uuid4())
    
    def register_user(self, username, email, password):
        """用户注册"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
                
                # 检查用户名和邮箱是否已存在
                cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
                if cursor.fetchone():
                    return False, "用户名或邮箱已存在"
                
                # 插入新用户
                password_hash = self.hash_password(password)
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, password_hash)
                )
                
                # 提交事务
                conn.commit()
                
            return True, "注册成功"
            
        except Exception as e:
            return False, f"注册失败: {str(e)}"
    
    def login_user(self, username, password):
        """用户登录"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
                
                password_hash = self.hash_password(password)
                cursor.execute(
                    "SELECT id, username, email, user_type FROM users WHERE username = ? AND password_hash = ? AND is_active = 1",
                    (username, password_hash)
                )
                
                user = cursor.fetchone()
                if user:
                    user_id = user[0]
                    
                    # 更新最后登录时间
                    cursor.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                        (user_id,)
                    )
                    
                    # 创建会话
                    session_id = self.generate_session_id()
                    expires_at = datetime.now() + timedelta(days=7)  # 7天过期
                    
                    cursor.execute(
                        "INSERT INTO sessions (user_id, session_id, expires_at) VALUES (?, ?, ?)",
                        (user_id, session_id, expires_at)
                    )
                    
                    # 提交事务
                    conn.commit()
                    
                    return True, {
                        'user_id': user_id,
                        'username': user[1],
                        'email': user[2],
                        'user_type': user[3],
                        'session_id': session_id
                    }
                else:
                    return False, "用户名或密码错误"
                
        except Exception as e:
            return False, f"登录失败: {str(e)}"
    
    def validate_session(self, session_id):
        """验证会话"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    """SELECT s.user_id, u.username, u.email, u.user_type 
                       FROM sessions s 
                       JOIN users u ON s.user_id = u.id 
                       WHERE s.session_id = ? AND s.is_active = 1 AND s.expires_at > CURRENT_TIMESTAMP""",
                    (session_id,)
                )
                
                result = cursor.fetchone()
            
            if result:
                return True, {
                    'user_id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'user_type': result[3],
                    'session_id': session_id
                }
            else:
                return False, "会话无效或已过期"
                
        except Exception as e:
            return False, f"会话验证失败: {str(e)}"
    
    def logout_user(self, session_id):
        """用户登出"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "UPDATE sessions SET is_active = 0 WHERE session_id = ?",
                    (session_id,)
                )
                
                # 提交事务
                conn.commit()
            
            return True, "登出成功"
            
        except Exception as e:
            return False, f"登出失败: {str(e)}"
    
    # 管理员功能方法
    def get_admin_statistics(self):
        """获取管理员统计数据"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
                
                # 总用户数
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                total_users = cursor.fetchone()[0]
                
                # 付费用户数
                cursor.execute("SELECT COUNT(*) FROM users WHERE user_type != 'free' AND is_active = 1")
                premium_users = cursor.fetchone()[0]
                
                # 今日活跃用户数
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM usage_records 
                    WHERE DATE(created_at) = ?
                """, (today,))
                today_active = cursor.fetchone()[0]
                
                # 总收入
                cursor.execute("""
                    SELECT COALESCE(SUM(amount), 0) FROM payment_records 
                    WHERE status = 'success'
                """)
                total_revenue = cursor.fetchone()[0]
                
                # 用户类型分布
                cursor.execute("""
                    SELECT user_type, COUNT(*) FROM users 
                    WHERE is_active = 1 
                    GROUP BY user_type
                """)
                user_type_stats = dict(cursor.fetchall())
                
                return {
                'total_users': total_users,
                'premium_users': premium_users,
                'today_active': today_active,
                'total_revenue': total_revenue,
                'user_type_stats': user_type_stats
            }
        except Exception as e:
            self.logger.error(f"获取统计数据失败", {"error": str(e)})
            return {
                'total_users': 0,
                'premium_users': 0,
                'today_active': 0,
                'total_revenue': 0,
                'user_type_stats': {}
            }
    
    def get_all_users_info(self):
        """获取所有用户信息"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT u.id, u.username, u.email, u.user_type, u.created_at, u.last_login,
                       COALESCE(usage_stats.total_usage, 0) as total_usage,
                       COALESCE(today_stats.today_usage, 0) as today_usage
                FROM users u
                LEFT JOIN (
                    SELECT user_id, COUNT(*) as total_usage
                    FROM usage_records
                    GROUP BY user_id
                ) usage_stats ON u.id = usage_stats.user_id
                LEFT JOIN (
                    SELECT user_id, COUNT(*) as today_usage
                    FROM usage_records
                    WHERE DATE(created_at) = DATE('now')
                    GROUP BY user_id
                ) today_stats ON u.id = today_stats.user_id
                WHERE u.is_active = 1
                ORDER BY u.created_at DESC
            """)
            
            # 从配置文件获取不同用户类型的每日限制
            limits = self.get_user_limits()
            
            columns = ['id', 'username', 'email', 'user_type', 'created_at', 'last_login', 'total_usage', 'today_usage']
            users = []
            for row in cursor.fetchall():
                user_dict = dict(zip(columns, row))
                # 计算剩余次数
                user_type = user_dict['user_type']
                today_usage = user_dict['today_usage'] or 0
                daily_limit = limits.get(user_type, 3)
                remaining_usage = max(0, daily_limit - today_usage)
                
                user_dict['daily_limit'] = daily_limit
                user_dict['remaining_usage'] = remaining_usage
                users.append(user_dict)
            
            return users
        except Exception as e:
            self.logger.error(f"获取用户信息失败", {"error": str(e)})
            return []
    
    def get_revenue_trend(self, days=30):
        """获取收入趋势数据"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT DATE(created_at) as date, SUM(amount) as revenue
                FROM payment_records
                WHERE payment_status = 'completed'
                  AND created_at >= DATE('now', '-{} days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """.format(days))
            
            result = [{'date': row[0], 'revenue': row[1]} for row in cursor.fetchall()]
            return result
        except Exception as e:
            self.logger.error(f"获取收入趋势失败", {"error": str(e)})
            return []
    
    def get_usage_trend(self, days=7):
        """获取使用量趋势数据"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as usage_count
                FROM usage_records
                WHERE created_at >= DATE('now', '-{} days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """.format(days))
            
            result = [{'date': row[0], 'usage_count': row[1]} for row in cursor.fetchall()]
            return result
        except Exception as e:
            self.logger.error(f"获取使用趋势失败", {"error": str(e)})
            return []
    
    def set_user_as_admin(self, username):
        """将用户设置为管理员"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
                
                # 检查用户是否存在
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                
                if not user:
                    return False, f"用户 {username} 不存在"
                
                # 更新用户类型为admin
                cursor.execute(
                    "UPDATE users SET user_type = 'admin' WHERE username = ?",
                    (username,)
                )
                
                # 提交事务
                conn.commit()
                
                return True, f"用户 {username} 已成功设置为管理员"
                
        except Exception as e:
            self.logger.error(f"设置管理员失败", {"error": str(e)})
            return False, f"设置管理员失败: {str(e)}"
    
    def get_department_usage(self):
        """获取科室使用分布"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT department, COUNT(*) as usage_count
                FROM usage_records
                WHERE department IS NOT NULL AND department != ''
                GROUP BY department
                ORDER BY usage_count DESC
            """)
            
            result = [{'department': row[0], 'usage_count': row[1]} for row in cursor.fetchall()]
            return result
        except Exception as e:
            self.logger.error(f"获取科室使用分布失败", {"error": str(e)})
            return []
    
    def get_payment_records(self):
        """获取付费记录"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, u.username, p.plan_type, p.amount, p.payment_method, 
                       p.payment_status, p.start_date, p.end_date, p.created_at
                FROM payment_records p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
            """)
            
            columns = ['id', 'username', 'plan_type', 'amount', 'payment_method', 
                      'payment_status', 'start_date', 'end_date', 'created_at']
            records = []
            for row in cursor.fetchall():
                record_dict = dict(zip(columns, row))
                records.append(record_dict)
            
            return records
        except Exception as e:
            self.logger.error(f"获取付费记录失败", {"error": str(e)})
            return []
    
    def record_usage(self, user_id, action_type, department=None, tokens_used=0):
        """记录使用情况"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO usage_records (user_id, action_type, department, tokens_used) VALUES (?, ?, ?, ?)",
                (user_id, action_type, department, tokens_used)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"记录使用情况失败", {"error": str(e), "user_id": user_id, "action_type": action_type})
            return False
    
    def get_daily_usage_count(self, user_id, action_type="consultation"):
        """获取今日使用次数"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                """SELECT COUNT(*) FROM usage_records 
                   WHERE user_id = ? AND action_type = ? AND DATE(created_at) = ?""",
                (user_id, action_type, today)
            )
            
            count = cursor.fetchone()[0]
            return count
            
        except Exception as e:
            self.logger.error(f"获取使用次数失败", {"error": str(e), "user_id": user_id, "action_type": action_type})
            return 0
    
    def check_usage_limit(self, user_id, user_type, action_type="consultation"):
        """检查使用限制"""
        daily_count = self.get_daily_usage_count(user_id, action_type)
        
        # 从配置文件获取不同用户类型的限制
        limits = self.get_user_limits()
        
        limit = limits.get(user_type, 3)
        return daily_count < limit, daily_count, limit
    
    def get_guest_daily_usage_count(self, ip_address, action_type="consultation"):
        """获取游客今日使用次数（基于IP地址）"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                """SELECT COUNT(*) FROM guest_usage_records 
                   WHERE ip_address = ? AND action_type = ? AND DATE(created_at) = ?""",
                (ip_address, action_type, today)
            )
            
            count = cursor.fetchone()[0]
            return count
            
        except Exception as e:
            self.logger.error(f"获取游客使用次数失败", {"error": str(e), "ip_address": ip_address, "action_type": action_type})
            return 0
    
    def record_guest_usage(self, ip_address, action_type, department=None, tokens_used=0):
        """记录游客使用情况"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO guest_usage_records (ip_address, action_type, department, tokens_used) VALUES (?, ?, ?, ?)",
                (ip_address, action_type, department, tokens_used)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"记录游客使用情况失败", {"error": str(e), "ip_address": ip_address, "action_type": action_type})
            return False
    
    def check_guest_usage_limit(self, ip_address, action_type="consultation"):
        """检查游客使用限制"""
        daily_count = self.get_guest_daily_usage_count(ip_address, action_type)
        
        # 从配置文件获取游客限制
        limits = self.get_user_limits()
        limit = limits.get('guest', 1)
        
        return daily_count < limit, daily_count, limit
    
    def get_user_stats(self, user_id):
        """获取用户统计信息"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
            
            # 总使用次数
            cursor.execute(
                "SELECT COUNT(*) FROM usage_records WHERE user_id = ?",
                (user_id,)
            )
            total_usage = cursor.fetchone()[0]
            
            # 今日使用次数
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                "SELECT COUNT(*) FROM usage_records WHERE user_id = ? AND DATE(created_at) = ?",
                (user_id, today)
            )
            today_usage = cursor.fetchone()[0]
            
            # 最常使用的科室
            cursor.execute(
                """SELECT department, COUNT(*) as count FROM usage_records 
                   WHERE user_id = ? AND department IS NOT NULL 
                   GROUP BY department ORDER BY count DESC LIMIT 1""",
                (user_id,)
            )
            favorite_dept = cursor.fetchone()
            
            return {
                'total_usage': total_usage,
                'today_usage': today_usage,
                'favorite_department': favorite_dept[0] if favorite_dept else None
            }
            
        except Exception as e:
            self.logger.error(f"获取用户统计失败", {"error": str(e), "user_id": user_id})
            return {
                'total_usage': 0,
                'today_usage': 0,
                'favorite_department': None
            }
    
    def upgrade_user(self, user_id, plan_type, amount):
        """升级用户"""
        try:
            with self.connection_pool.connection() as conn:
                cursor = conn.cursor()
            
            # 更新用户类型
            new_user_type = 'premium' if plan_type in ['monthly', 'quarterly', 'yearly'] else 'free'
            cursor.execute(
                "UPDATE users SET user_type = ? WHERE id = ?",
                (new_user_type, user_id)
            )
            
            # 记录付费记录
            start_date = datetime.now()
            if plan_type == 'monthly':
                end_date = start_date + timedelta(days=30)
            elif plan_type == 'quarterly':
                end_date = start_date + timedelta(days=90)
            elif plan_type == 'yearly':
                end_date = start_date + timedelta(days=365)
            else:
                end_date = start_date + timedelta(days=30)
            
            cursor.execute(
                """INSERT INTO payment_records (user_id, plan_type, amount, payment_status, start_date, end_date) 
                   VALUES (?, ?, ?, 'completed', ?, ?)""",
                (user_id, plan_type, amount, start_date, end_date)
            )
            
            # 提交事务
            conn.commit()
            
            return True, "升级成功"
            
        except Exception as e:
            self.logger.error(f"用户升级失败", {"error": str(e), "user_id": user_id, "plan_type": plan_type})
            return False, f"升级失败: {str(e)}"