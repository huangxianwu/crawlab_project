#!/usr/bin/env python3
"""
电商爬虫主入口文件
MVP版本 - 基础功能验证
"""
import sys
import os
import logging
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from utils.logger import setup_logger
from utils.database import get_db_manager
from models.product import ProductData


def main():
    """主函数"""
    print("🚀 电商爬虫系统启动")
    print("=" * 50)
    
    # 初始化日志
    logger = setup_logger()
    logger.info("爬虫系统启动")
    
    # 显示配置信息
    print("📋 系统配置信息:")
    print(f"  目标网站: {Config.TARGET_URL}")
    print(f"  数据库: {Config.MONGO_URI}")
    print(f"  数据库名: {Config.DATABASE_NAME}")
    print(f"  集合名: {Config.COLLECTION_NAME}")
    print(f"  最小延时: {Config.MIN_DELAY}秒")
    print(f"  最大延时: {Config.MAX_DELAY}秒")
    print(f"  最大重试: {Config.MAX_RETRY}次")
    
    # 测试数据库连接
    print("\n🔗 测试数据库连接...")
    db_manager = get_db_manager()
    
    if db_manager.connect():
        print("✅ 数据库连接成功")
        logger.info("数据库连接成功")
        
        # 显示数据库统计信息
        stats = db_manager.get_statistics()
        if "error" not in stats:
            print(f"  当前数据总数: {stats['total_products']}条")
            print(f"  滑块成功率: {stats['slider_success_rate']}%")
        
        db_manager.disconnect()
    else:
        print("❌ 数据库连接失败")
        logger.error("数据库连接失败")
        return
    
    # 显示项目结构
    print("\n📁 项目结构:")
    print("  crawler-project/")
    print("  ├── main.py              # 主入口文件")
    print("  ├── config.py            # 配置管理")
    print("  ├── models/              # 数据模型")
    print("  │   ├── __init__.py")
    print("  │   └── product.py       # 商品数据模型")
    print("  ├── utils/               # 工具类")
    print("  │   ├── __init__.py")
    print("  │   ├── database.py      # 数据库操作")
    print("  │   └── logger.py        # 日志工具")
    print("  ├── handlers/            # 处理器")
    print("  │   └── __init__.py")
    print("  ├── requirements.txt     # 依赖包")
    print("  └── logs/               # 日志目录")
    
    print("\n✅ 基础框架初始化完成")
    logger.info("基础框架初始化完成")
    
    print("\n📝 下一步:")
    print("  1. 实现WebDriver管理器")
    print("  2. 添加商品搜索功能")
    print("  3. 集成滑块处理逻辑")
    print("  4. 完善数据采集流程")


if __name__ == "__main__":
    main()