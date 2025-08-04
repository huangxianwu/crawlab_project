#!/usr/bin/env python3
"""
电商爬虫主入口文件
增强版本 - 包含商品链接、店铺名称、评论时间等完整字段
"""
import sys
import os
import logging
from datetime import datetime

# 路径修复 - 确保能找到项目模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import Config
from utils.logger import setup_logger
from utils.database import get_db_manager
from models.product import ProductData
from tests.demo.reference_based_scraper import ReferenceBasedScraper


def main():
    """主函数"""
    print("🚀 电商爬虫系统启动 - 增强版本")
    print("=" * 60)
    
    # 初始化日志
    logger = setup_logger()
    logger.info("爬虫系统启动 - 增强版本")
    
    # 显示配置信息
    print("📋 系统配置信息:")
    print(f"  目标网站: {Config.TARGET_URL}")
    print(f"  数据库: {Config.MONGO_URI}")
    print(f"  数据库名: {Config.DATABASE_NAME}")
    print(f"  集合名: {Config.COLLECTION_NAME}")
    print(f"  最小延时: {Config.MIN_DELAY}秒")
    print(f"  最大延时: {Config.MAX_DELAY}秒")
    print(f"  最大重试: {Config.MAX_RETRY}次")
    
    # 显示增强功能
    print("\n🔍 增强字段采集功能:")
    print("  ✅ 商品链接 (product_url)")
    print("  ✅ 店铺名称 (shop_name)")
    print("  ✅ 评论时间 (latest_review_fmt, earliest_review_fmt)")
    print("  ✅ 商品图片 (product_image)")
    print("  ✅ 商品描述 (desc_detail)")
    print("  ✅ 销量信息 (sold_count)")
    print("  ✅ 评分信息 (product_rating)")
    
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
    print("  │   └── product.py       # 商品数据模型 (增强版)")
    print("  ├── utils/               # 工具类")
    print("  │   ├── __init__.py")
    print("  │   ├── database.py      # 数据库操作")
    print("  │   └── logger.py        # 日志工具")
    print("  ├── handlers/            # 处理器")
    print("  │   ├── __init__.py")
    print("  │   ├── slider.py        # 滑块处理")
    print("  │   └── extractor.py     # 数据提取")
    print("  ├── tests/               # 测试代码")
    print("  │   ├── unit/           # 单元测试")
    print("  │   ├── integration/    # 集成测试")
    print("  │   └── demo/           # 演示代码")
    print("  ├── requirements.txt     # 依赖包")
    print("  └── logs/               # 日志目录")
    
    print("\n✅ 增强框架初始化完成")
    logger.info("增强框架初始化完成")
    
    # 演示增强功能
    print("\n🎯 演示增强字段采集功能:")
    print("  运行示例: python tests/demo/reference_based_scraper.py")
    print("  验证字段: python test_enhanced_fields_simple.py")
    print("  检查数据: python check_product_fields.py")
    
    print("\n📝 下一步:")
    print("  1. 运行增强字段采集测试")
    print("  2. 验证所有字段完整性")
    print("  3. 集成到生产环境")
    print("  4. 优化性能和稳定性")


def run_enhanced_scraping_demo():
    """运行增强字段采集演示"""
    print("\n🎯 运行增强字段采集演示")
    print("=" * 60)
    
    try:
        # 初始化采集器
        scraper = ReferenceBasedScraper()
        print("✅ 采集器初始化成功")
        
        # 执行采集
        keyword = "phone case"
        page_count = 1
        print(f"📦 开始采集商品数据 (关键词: {keyword}, 页数: {page_count})")
        
        products = scraper.scrape_keyword_products(keyword, page_count)
        print(f"🎉 采集完成，共获取 {len(products)} 个商品")
        
        # 显示样本数据
        if products:
            print("\n📊 样本商品数据:")
            sample_product = products[0]
            print(f"  商品ID: {sample_product.get('product_id')}")
            print(f"  商品标题: {sample_product.get('title', '')[:50]}...")
            print(f"  商品价格: ${sample_product.get('current_price')}")
            print(f"  商品链接: {sample_product.get('product_url')}")
            print(f"  店铺名称: {sample_product.get('shop_name')}")
            print(f"  最近评价时间: {sample_product.get('latest_review_fmt') or '暂无'}")
            print(f"  最早评价时间: {sample_product.get('earliest_review_fmt') or '暂无'}")
        
        scraper.close()
        print("\n✅ 增强字段采集演示完成")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


if __name__ == "__main__":
    main()
    
    # 可选：运行演示
    # run_enhanced_scraping_demo()