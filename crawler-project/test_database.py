#!/usr/bin/env python3
"""
数据库功能测试脚本
验证MongoDB连接和基础CRUD操作
"""
import sys
import logging
from datetime import datetime

# 添加项目路径
sys.path.append('.')

from models.product import ProductData
from utils.database import DatabaseManager


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/database_test.log', encoding='utf-8')
        ]
    )


def test_database_connection():
    """测试数据库连接"""
    print("=" * 50)
    print("测试1: 数据库连接")
    print("=" * 50)
    
    db_manager = DatabaseManager()
    
    # 测试连接
    if db_manager.connect():
        print("✅ MongoDB连接成功")
        return db_manager
    else:
        print("❌ MongoDB连接失败")
        return None


def test_data_insertion(db_manager: DatabaseManager):
    """测试数据插入"""
    print("\n" + "=" * 50)
    print("测试2: 数据插入")
    print("=" * 50)
    
    # 创建测试数据
    test_product = ProductData(
        keyword="测试",
        title="测试商品标题",
        scraped_at=datetime.now(),
        slider_encountered=False,
        slider_solved=False
    )
    
    print(f"准备插入测试数据: {test_product}")
    
    # 插入数据
    if db_manager.insert_product(test_product):
        print("✅ 测试数据插入成功")
        return True
    else:
        print("❌ 测试数据插入失败")
        return False


def test_data_query(db_manager: DatabaseManager):
    """测试数据查询"""
    print("\n" + "=" * 50)
    print("测试3: 数据查询")
    print("=" * 50)
    
    # 查询测试数据
    products = db_manager.find_products_by_keyword("测试")
    
    if products:
        print(f"✅ 查询成功，找到 {len(products)} 条数据:")
        for i, product in enumerate(products, 1):
            print(f"  {i}. {product}")
        return True
    else:
        print("❌ 查询失败或无数据")
        return False


def test_batch_insertion(db_manager: DatabaseManager):
    """测试批量插入"""
    print("\n" + "=" * 50)
    print("测试4: 批量数据插入")
    print("=" * 50)
    
    # 创建批量测试数据
    test_products = [
        ProductData(
            keyword="手机壳",
            title="苹果iPhone14手机壳透明防摔",
            scraped_at=datetime.now(),
            slider_encountered=True,
            slider_solved=True
        ),
        ProductData(
            keyword="手机壳",
            title="华为mate50手机壳硅胶软壳",
            scraped_at=datetime.now(),
            slider_encountered=False,
            slider_solved=False
        ),
        ProductData(
            keyword="数据线",
            title="苹果原装数据线Lightning充电线",
            scraped_at=datetime.now(),
            slider_encountered=True,
            slider_solved=False
        )
    ]
    
    print(f"准备批量插入 {len(test_products)} 条测试数据")
    
    # 批量插入
    inserted_count = db_manager.insert_products(test_products)
    
    if inserted_count == len(test_products):
        print(f"✅ 批量插入成功: {inserted_count} 条数据")
        return True
    else:
        print(f"❌ 批量插入部分失败: 期望{len(test_products)}条，实际{inserted_count}条")
        return False


def test_statistics(db_manager: DatabaseManager):
    """测试统计功能"""
    print("\n" + "=" * 50)
    print("测试5: 统计信息")
    print("=" * 50)
    
    stats = db_manager.get_statistics()
    
    if "error" not in stats:
        print("✅ 统计信息获取成功:")
        print(f"  总商品数: {stats['total_products']}")
        print(f"  遇到滑块: {stats['slider_encountered']}")
        print(f"  滑块成功: {stats['slider_solved']}")
        print(f"  成功率: {stats['slider_success_rate']}%")
        print("  关键词统计:")
        for keyword_stat in stats['keyword_stats']:
            print(f"    {keyword_stat['_id']}: {keyword_stat['count']}条")
        return True
    else:
        print(f"❌ 统计信息获取失败: {stats['error']}")
        return False


def test_all_products_query(db_manager: DatabaseManager):
    """测试查询所有数据"""
    print("\n" + "=" * 50)
    print("测试6: 查询所有数据")
    print("=" * 50)
    
    all_products = db_manager.find_all_products(limit=10)
    
    if all_products:
        print(f"✅ 查询所有数据成功，共 {len(all_products)} 条:")
        for i, product in enumerate(all_products, 1):
            print(f"  {i}. [{product.keyword}] {product.title}")
        return True
    else:
        print("❌ 查询所有数据失败或无数据")
        return False


def main():
    """主测试函数"""
    print("开始数据库功能测试...")
    
    # 设置日志
    setup_logging()
    
    # 创建日志目录
    import os
    os.makedirs('logs', exist_ok=True)
    
    # 测试结果统计
    test_results = []
    
    # 1. 测试数据库连接
    db_manager = test_database_connection()
    test_results.append(db_manager is not None)
    
    if not db_manager:
        print("\n❌ 数据库连接失败，无法继续测试")
        return
    
    try:
        # 2. 测试数据插入
        test_results.append(test_data_insertion(db_manager))
        
        # 3. 测试数据查询
        test_results.append(test_data_query(db_manager))
        
        # 4. 测试批量插入
        test_results.append(test_batch_insertion(db_manager))
        
        # 5. 测试统计功能
        test_results.append(test_statistics(db_manager))
        
        # 6. 测试查询所有数据
        test_results.append(test_all_products_query(db_manager))
        
    finally:
        # 关闭数据库连接
        db_manager.disconnect()
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"通过测试: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！数据库功能正常")
    else:
        print("⚠️  部分测试失败，请检查配置和环境")
    
    print("\n验证标准检查:")
    print("✅ 运行测试脚本，成功连接到MongoDB数据库" if test_results[0] else "❌ 数据库连接失败")
    print("✅ 插入测试数据成功" if test_results[1] else "❌ 插入测试数据失败")
    print("✅ 查询数据库，能够正确返回刚插入的测试数据" if test_results[2] else "❌ 查询测试数据失败")
    print("✅ 批量插入和统计功能正常" if all(test_results[3:]) else "❌ 批量操作或统计功能异常")


if __name__ == "__main__":
    main()