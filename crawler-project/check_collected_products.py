#!/usr/bin/env python3
"""
查询采集的商品信息
检查商品数据包含的字段
"""
import sys
import os
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import get_db_manager
from utils.logger import setup_logger

def check_collected_products():
    """查询采集的商品信息"""
    print("🔍 查询采集的商品信息")
    print("=" * 60)
    
    # 初始化日志和数据库
    logger = setup_logger('check_products')
    db_manager = get_db_manager()
    
    try:
        # 连接数据库
        if not db_manager.connect():
            print("❌ 数据库连接失败")
            return
        
        print("✅ 数据库连接成功")
        
        # 获取数据库统计信息
        stats = db_manager.get_statistics()
        if "error" not in stats:
            print(f"📊 数据库统计:")
            print(f"  总商品数: {stats['total_products']} 条")
            print(f"  滑块成功率: {stats['slider_success_rate']}%")
        
        # 查询最近采集的商品（按创建时间排序）
        print(f"\n🔍 查询最近采集的商品...")
        
        # 使用MongoDB查询最近的商品
        collection = db_manager.collection
        if collection is not None:
            # 查询最近30条商品记录
            recent_products = list(collection.find().sort("scraped_at", -1).limit(30))
            
            if recent_products:
                print(f"✅ 找到 {len(recent_products)} 条最近的商品记录")
                
                # 分析字段结构
                print(f"\n📋 商品数据字段分析:")
                
                # 获取第一个商品的所有字段
                sample_product = recent_products[0]
                all_fields = list(sample_product.keys())
                
                print(f"📊 商品记录包含 {len(all_fields)} 个字段:")
                for i, field in enumerate(all_fields, 1):
                    field_value = sample_product.get(field)
                    field_type = type(field_value).__name__
                    
                    # 显示字段值的预览
                    if isinstance(field_value, str) and len(field_value) > 50:
                        preview = field_value[:50] + "..."
                    else:
                        preview = str(field_value)
                    
                    print(f"  {i:2d}. {field:<20} ({field_type:<10}) = {preview}")
                
                # 显示最近采集的商品样例
                print(f"\n📦 最近采集的商品样例:")
                print("-" * 80)
                
                for i, product in enumerate(recent_products[:5], 1):
                    print(f"\n商品 {i}:")
                    print(f"  ID: {product.get('_id', 'N/A')}")
                    print(f"  商品ID: {product.get('product_id', 'N/A')}")
                    print(f"  标题: {product.get('title', 'N/A')}")
                    print(f"  关键词: {product.get('keyword', 'N/A')}")
                    print(f"  价格: ${product.get('current_price', 0)}")
                    print(f"  原价: ${product.get('origin_price', 0)}")
                    print(f"  店铺: {product.get('shop_name', 'N/A')}")
                    print(f"  销量: {product.get('sold_count', 0)}")
                    print(f"  评分: {product.get('product_rating', 0)}⭐")
                    print(f"  图片: {product.get('product_image', 'N/A')[:50]}...")
                    print(f"  链接: {product.get('product_url', 'N/A')[:50]}...")
                    print(f"  采集时间: {product.get('scraped_at', 'N/A')}")
                    print(f"  滑块处理: {product.get('slider_encountered', False)}")
                
                # 按关键词分组统计
                print(f"\n📊 按关键词分组统计:")
                keyword_stats = {}
                for product in recent_products:
                    keyword = product.get('keyword', 'unknown')
                    if keyword not in keyword_stats:
                        keyword_stats[keyword] = 0
                    keyword_stats[keyword] += 1
                
                for keyword, count in keyword_stats.items():
                    print(f"  {keyword}: {count} 个商品")
                
                # 价格分析
                print(f"\n💰 价格分析:")
                prices = [float(p.get('current_price', 0)) for p in recent_products if p.get('current_price')]
                if prices:
                    print(f"  最低价格: ${min(prices):.2f}")
                    print(f"  最高价格: ${max(prices):.2f}")
                    print(f"  平均价格: ${sum(prices)/len(prices):.2f}")
                
                # 检查字段完整性
                print(f"\n🔍 字段完整性检查:")
                important_fields = [
                    'product_id', 'title', 'current_price', 'shop_name', 
                    'product_image', 'product_url', 'sold_count', 'product_rating'
                ]
                
                for field in important_fields:
                    filled_count = sum(1 for p in recent_products if p.get(field) and str(p.get(field)).strip())
                    percentage = (filled_count / len(recent_products)) * 100
                    status = "✅" if percentage > 80 else "⚠️" if percentage > 50 else "❌"
                    print(f"  {status} {field:<20}: {filled_count:2d}/{len(recent_products)} ({percentage:5.1f}%)")
                
                # 导出样例数据到JSON文件
                print(f"\n📄 导出样例数据...")
                sample_data = []
                for product in recent_products[:10]:
                    # 转换ObjectId为字符串
                    product_dict = {}
                    for key, value in product.items():
                        if key == '_id':
                            product_dict[key] = str(value)
                        elif isinstance(value, datetime):
                            product_dict[key] = value.isoformat()
                        else:
                            product_dict[key] = value
                    sample_data.append(product_dict)
                
                # 保存到文件
                output_file = f"sample_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(sample_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ 样例数据已导出到: {output_file}")
                
            else:
                print("⚠️ 未找到商品记录")
        else:
            print("❌ 无法访问数据库集合")
        
    except Exception as e:
        print(f"❌ 查询过程中发生错误: {e}")
        logger.error(f"查询失败: {e}")
        
    finally:
        # 清理资源
        if db_manager:
            db_manager.disconnect()
            print(f"\n✅ 数据库连接已关闭")

def main():
    """主函数"""
    print("TikTok Shop商品数据查询工具")
    print("查询最近采集的商品信息和字段结构")
    print()
    
    check_collected_products()
    
    print(f"\n" + "=" * 60)
    print("🎉 商品数据查询完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()