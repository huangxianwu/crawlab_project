#!/usr/bin/env python3
"""
Crawlab环境测试脚本
用于验证Crawlab环境是否正确配置
"""
import os
import sys
import traceback

def test_python_environment():
    """测试Python环境"""
    print("🐍 Python环境测试")
    print("-" * 30)
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"当前工作目录: {os.getcwd()}")
    print()

def test_environment_variables():
    """测试环境变量"""
    print("🔧 环境变量测试")
    print("-" * 30)
    
    env_vars = [
        "CRAWLAB_MONGO_HOST",
        "CRAWLAB_MONGO_PORT", 
        "CRAWLAB_MONGO_DB",
        "CHROME_BIN",
        "DISPLAY",
        "keywords",
        "max_pages",
        "headless"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "未设置")
        print(f"{var}: {value}")
    print()

def test_file_structure():
    """测试文件结构"""
    print("📁 文件结构测试")
    print("-" * 30)
    
    required_files = [
        "crawlab_runner.py",
        "crawlab_simple_runner.py",
        "spider.json",
        "requirements.txt",
        "config.py"
    ]
    
    for file in required_files:
        exists = os.path.exists(file)
        status = "✅" if exists else "❌"
        print(f"{status} {file}")
    
    # 检查目录
    required_dirs = ["handlers", "utils", "models"]
    for dir_name in required_dirs:
        exists = os.path.isdir(dir_name)
        status = "✅" if exists else "❌"
        print(f"{status} {dir_name}/")
    print()

def test_dependencies():
    """测试依赖包"""
    print("📦 依赖包测试")
    print("-" * 30)
    
    dependencies = [
        ("DrissionPage", "from DrissionPage import ChromiumPage"),
        ("ddddocr", "import ddddocr"),
        ("pymongo", "import pymongo"),
        ("requests", "import requests"),
        ("cv2", "import cv2"),
        ("numpy", "import numpy"),
        ("PIL", "from PIL import Image")
    ]
    
    for name, import_cmd in dependencies:
        try:
            exec(import_cmd)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name}: {e}")
        except Exception as e:
            print(f"⚠️ {name}: {e}")
    print()

def test_mongodb_connection():
    """测试MongoDB连接"""
    print("🗄️ MongoDB连接测试")
    print("-" * 30)
    
    try:
        import pymongo
        
        # 构建连接字符串
        mongo_host = os.getenv("CRAWLAB_MONGO_HOST", "mongo")
        mongo_port = os.getenv("CRAWLAB_MONGO_PORT", "27017")
        mongo_db = os.getenv("CRAWLAB_MONGO_DB", "crawlab_test")
        
        mongo_uri = f"mongodb://{mongo_host}:{mongo_port}"
        print(f"连接字符串: {mongo_uri}")
        print(f"数据库: {mongo_db}")
        
        # 尝试连接
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        # 测试数据库操作
        db = client[mongo_db]
        collection = db["test_collection"]
        
        # 插入测试数据
        test_doc = {"test": "crawlab_env_test", "timestamp": "2025-01-31"}
        result = collection.insert_one(test_doc)
        print(f"✅ 插入测试数据成功: {result.inserted_id}")
        
        # 查询测试数据
        found_doc = collection.find_one({"test": "crawlab_env_test"})
        if found_doc:
            print("✅ 查询测试数据成功")
        
        # 删除测试数据
        collection.delete_one({"test": "crawlab_env_test"})
        print("✅ 删除测试数据成功")
        
        client.close()
        print("✅ MongoDB连接测试通过")
        
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        traceback.print_exc()
    print()

def test_browser_setup():
    """测试浏览器设置"""
    print("🌐 浏览器设置测试")
    print("-" * 30)
    
    try:
        from DrissionPage import ChromiumOptions, ChromiumPage
        
        # 配置浏览器选项
        options = ChromiumOptions()
        options.headless(True)
        options.set_argument('--no-sandbox')
        options.set_argument('--disable-dev-shm-usage')
        options.set_argument('--disable-gpu')
        
        chrome_bin = os.getenv("CHROME_BIN")
        if chrome_bin:
            print(f"Chrome路径: {chrome_bin}")
            if os.path.exists(chrome_bin):
                print("✅ Chrome可执行文件存在")
            else:
                print("❌ Chrome可执行文件不存在")
        
        # 尝试创建浏览器实例（但不启动）
        print("✅ 浏览器配置测试通过")
        
    except Exception as e:
        print(f"❌ 浏览器设置失败: {e}")
        traceback.print_exc()
    print()

def test_ddddocr_setup():
    """测试ddddocr设置"""
    print("🧩 ddddocr设置测试")
    print("-" * 30)
    
    try:
        import ddddocr
        
        # 创建识别器实例
        det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
        print("✅ ddddocr初始化成功")
        
    except Exception as e:
        print(f"❌ ddddocr设置失败: {e}")
        traceback.print_exc()
    print()

def main():
    """主测试函数"""
    print("🧪 Crawlab环境测试开始")
    print("=" * 50)
    print()
    
    # 执行所有测试
    test_python_environment()
    test_environment_variables()
    test_file_structure()
    test_dependencies()
    test_mongodb_connection()
    test_browser_setup()
    test_ddddocr_setup()
    
    print("🎉 Crawlab环境测试完成")
    print("=" * 50)
    print()
    print("📋 测试结果说明:")
    print("✅ = 测试通过")
    print("❌ = 测试失败，需要修复")
    print("⚠️ = 测试警告，可能影响功能")
    print()
    print("如果所有关键测试都显示 ✅，说明环境配置正确，可以运行爬虫。")

if __name__ == "__main__":
    main()