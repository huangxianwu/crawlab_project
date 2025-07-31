#!/usr/bin/env python3
"""
数据库功能演示脚本
展示基本的数据模型和存储功能
"""
import sys
from datetime import datetime

# 添加项目路径
sys.path.append('.')

from models.product import ProductData
from utils.database import get_db_manager


def main():
    """演示数据库基本功能"""
    print("🚀 数据库功能演示")
    print("=" * 40)
    
    # 获取数据库管理器
    db_manager = get_db_manager()
    
    # 连接数据库
    if not db_manager.connect():
        print("❌ 数据库连接失败")
        return
    
    print("✅ 数据库连接成功")
    
    # 创建示例商品数据
    sample_product = ProductData(
        keyword="演示关键词",
        title="演示商品标题 - 高质量商品",
        scraped_at=datetime.now(),
        slider_encountered=True,
        slider_solved=True
    )
    
    print(f"\n📦 创建商品数据: {sample_product}")
    
    # 插入数据
    if db_manager.insert_product(sample_product):
        print("✅ 数据插入成功")
    else:
        print("❌ 数据插入失败")
        return
    
    # 查询数据
    print(f"\n🔍 查询关键词 '{sample_product.keyword}' 的商品:")
    products = db_manager.find_products_by_keyword(sample_product.keyword)
    
    for i, product in enumerate(products, 1):
        print(f"  {i}. {product.title}")
        print(f"     采集时间: {product.scraped_at}")
        print(f"     滑块处理: {'成功' if product.slider_solved else '失败' if product.slider_encountered else '未遇到'}")
    
    # 显示统计信息
    print(f"\n📊 数据库统计信息:")
    stats = db_manager.get_statistics()
    
    if "error" not in stats:
        print(f"  总商品数: {stats['total_products']}")
        print(f"  滑块成功率: {stats['slider_success_rate']}%")
        print("  热门关键词:")
        for keyword_stat in stats['keyword_stats'][:3]:
            print(f"    {keyword_stat['_id']}: {keyword_stat['count']}条")
    
    # 关闭连接
    db_manager.disconnect()
    print("\n✅ 演示完成")


if __name__ == "__main__":
    main()