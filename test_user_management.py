#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块测试脚本
用于测试用户注册、登录、会话管理等功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.user_manager import UserManager

def test_user_management():
    """测试用户管理功能"""
    print("🧪 开始测试用户管理模块...\n")
    
    # 初始化用户管理器
    user_manager = UserManager()
    print("✅ 用户管理器初始化成功")
    
    # 测试用户注册
    print("\n📝 测试用户注册...")
    success, message = user_manager.register_user(
        username="test_user",
        email="test@example.com",
        password="test123"
    )
    print(f"注册结果: {message}")
    
    # 测试重复注册
    print("\n🔄 测试重复注册...")
    success, message = user_manager.register_user(
        username="test_user",
        email="test@example.com",
        password="test123"
    )
    print(f"重复注册结果: {message}")
    
    # 测试用户登录
    print("\n🔐 测试用户登录...")
    success, result = user_manager.login_user(
        username="test_user",
        password="test123"
    )
    if success:
        print(f"登录成功: {result['username']} ({result['user_type']})")
        session_id = result['session_id']
        user_id = result['user_id']
    else:
        print(f"登录失败: {result}")
        return
    
    # 测试会话验证
    print("\n🔍 测试会话验证...")
    valid, user_info = user_manager.validate_session(session_id)
    if valid:
        print(f"会话有效: {user_info['username']}")
    else:
        print(f"会话无效: {user_info}")
    
    # 测试使用记录
    print("\n📊 测试使用记录...")
    user_manager.record_usage(user_id, "consultation", "内科", 100)
    user_manager.record_usage(user_id, "consultation", "外科", 150)
    user_manager.record_usage(user_id, "consultation", "内科", 120)
    print("使用记录添加成功")
    
    # 测试使用限制检查
    print("\n⏰ 测试使用限制检查...")
    can_use, daily_count, limit = user_manager.check_usage_limit(user_id, "free")
    print(f"免费用户使用情况: {daily_count}/{limit}, 可继续使用: {can_use}")
    
    # 测试用户统计
    print("\n📈 测试用户统计...")
    stats = user_manager.get_user_stats(user_id)
    print(f"用户统计: {stats}")
    
    # 测试用户升级
    print("\n💎 测试用户升级...")
    success, message = user_manager.upgrade_user(user_id, "monthly", 39.0)
    print(f"升级结果: {message}")
    
    # 再次检查使用限制
    print("\n⏰ 升级后使用限制检查...")
    can_use, daily_count, limit = user_manager.check_usage_limit(user_id, "premium")
    print(f"高级用户使用情况: {daily_count}/{limit}, 可继续使用: {can_use}")
    
    # 测试用户登出
    print("\n🚪 测试用户登出...")
    success, message = user_manager.logout_user(session_id)
    print(f"登出结果: {message}")
    
    # 验证登出后会话状态
    print("\n🔍 验证登出后会话状态...")
    valid, user_info = user_manager.validate_session(session_id)
    if valid:
        print(f"会话仍然有效: {user_info['username']}")
    else:
        print(f"会话已失效: {user_info}")
    
    print("\n🎉 用户管理模块测试完成！")

def test_multiple_users():
    """测试多用户场景"""
    print("\n👥 测试多用户场景...")
    
    user_manager = UserManager()
    
    # 创建多个测试用户
    users = [
        {"username": "doctor_zhang", "email": "zhang@hospital.com", "password": "doctor123"},
        {"username": "patient_li", "email": "li@email.com", "password": "patient123"},
        {"username": "nurse_wang", "email": "wang@hospital.com", "password": "nurse123"}
    ]
    
    for user in users:
        success, message = user_manager.register_user(
            user["username"], user["email"], user["password"]
        )
        print(f"注册用户 {user['username']}: {message}")
    
    # 模拟用户活动
    for user in users:
        success, result = user_manager.login_user(user["username"], user["password"])
        if success:
            user_id = result['user_id']
            # 模拟不同的使用情况
            for i in range(2):
                user_manager.record_usage(user_id, "consultation", "内科")
            print(f"用户 {user['username']} 模拟使用完成")
    
    print("多用户测试完成")

if __name__ == "__main__":
    try:
        test_user_management()
        test_multiple_users()
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()