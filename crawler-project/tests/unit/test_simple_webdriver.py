#!/usr/bin/env python3
"""
简单WebDriver测试
验证基本功能是否正常
"""
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入是否正常"""
    try:
        print("测试导入...")
        from config import Config
        print("✅ Config导入成功")
        
        from utils.logger import setup_logger
        print("✅ Logger导入成功")
        
        from utils.webdriver import WebDriverManager
        print("✅ WebDriverManager导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_webdriver_creation():
    """测试WebDriver创建"""
    try:
        print("\n测试WebDriver创建...")
        from utils.webdriver import WebDriverManager
        
        # 创建WebDriver管理器
        manager = WebDriverManager(headless=True)  # 使用无头模式避免弹窗
        print("✅ WebDriverManager创建成功")
        
        # 创建驱动
        driver = manager.create_driver()
        print("✅ Chrome驱动创建成功")
        
        # 测试简单页面访问
        driver.get("https://www.google.com")
        print(f"✅ 页面访问成功，标题: {driver.title}")
        
        # 清理
        manager.close_driver()
        print("✅ 驱动关闭成功")
        
        return True
    except Exception as e:
        print(f"❌ WebDriver测试失败: {e}")
        return False

def main():
    print("🚀 简单WebDriver功能测试")
    print("=" * 40)
    
    # 测试1: 导入测试
    result1 = test_imports()
    
    if result1:
        # 测试2: WebDriver创建测试
        result2 = test_webdriver_creation()
    else:
        result2 = False
    
    print("\n" + "=" * 40)
    print("📊 测试结果:")
    print(f"导入测试: {'✅ 通过' if result1 else '❌ 失败'}")
    print(f"WebDriver测试: {'✅ 通过' if result2 else '❌ 失败'}")
    
    if result1 and result2:
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 部分测试失败")

if __name__ == "__main__":
    main()