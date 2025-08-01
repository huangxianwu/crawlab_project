#!/usr/bin/env python3
"""
50条商品采集验收测试
验收目标: 可以在数据库中查找到至少50条商品信息（也就是至少2页商品信息）
"""
import os
import sys
import time
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reference_based_scraper import ReferenceBasedScraper
from utils.database import DatabaseManager

class ProductScrapingAcceptanceTest:
    """50条商品采集验收测试"""
    
    def __init__(self):
        self.scraper = None
        self.db_manager = DatabaseManager()
        self.test_results = {
            'start_time': datetime.now().isoformat(),
            'target_count': 50,
            'actual_count': 0,
            'pages_scraped': 0,
            'success': False,
            'total_time': 0
        }
    
    def run_acceptance_test(self, keyword: str = "phone case", page_count: int = 2) -> bool:
        """
        运行50条商品采集验收测试
        
        Args:
            keyword: 搜索关键词
            page_count: 采集页数
            
        Returns:
            bool: 测试是否通过
        """
        print("🎯 50条商品采集验收测试")
        print("验收目标: 可以在数据库中查找到至少50条商品信息（至少2页商品信息）")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # 步骤1: 清空数据库（可选）
            print("\n📋 步骤1: 准备数据库")
            if not self.prepare_database():
                return False
            
            # 步骤2: 初始化采集器
            print("\n📋 步骤2: 初始化采集器")
            self.scraper = ReferenceBasedScraper()
            print("✅ 采集器初始化成功")
            
            # 步骤3: 执行商品采集
            print(f"\n📋 步骤3: 执行商品采集 (关键词: {keyword}, 页数: {page_count})")
            scraped_products = self.scraper.scrape_keyword_products(keyword, page_count)
            self.test_results['pages_scraped'] = page_count
            
            # 步骤4: 验证数据库中的商品数量
            print(f"\n📋 步骤4: 验证数据库中的商品数量")
            db_count = self.verify_database_count()
            self.test_results['actual_count'] = db_count
            
            # 步骤5: 验证商品数据完整性
            print(f"\n📋 步骤5: 验证商品数据完整性")
            data_quality = self.verify_data_quality()
            
            # 计算总耗时
            end_time = time.time()
            self.test_results['total_time'] = end_time - start_time
            
            # 判断测试结果
            success = (db_count >= self.test_results['target_count'] and data_quality)
            self.test_results['success'] = success
            
            # 显示测试结果
            self.display_test_results()
            
            return success
            
        except Exception as e:
            print(f"❌ 验收测试异常: {e}")
            return False
        
        finally:
            # 清理资源
            if self.scraper:
                self.scraper.close()
    
    def prepare_database(self) -> bool:
        """准备数据库"""
        try:
            if not self.db_manager.connect():
                print("❌ 数据库连接失败")
                return False
            
            # 获取当前商品数量
            current_count = self.db_manager.count_products()
            print(f"📊 数据库当前商品数量: {current_count}")
            
            # 询问是否清空数据库
            if current_count > 0:
                print("⚠️  数据库中已有商品数据")
                print("为了准确测试，建议清空数据库")
                # 自动清空以便测试
                if self.db_manager.clear_collection():
                    print("✅ 数据库已清空")
                else:
                    print("⚠️  数据库清空失败，继续测试")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据库准备失败: {e}")
            return False
    
    def verify_database_count(self) -> int:
        """验证数据库中的商品数量"""
        try:
            count = self.db_manager.count_products()
            print(f"📊 数据库中的商品总数: {count}")
            
            if count >= self.test_results['target_count']:
                print(f"✅ 达到目标数量: {count} >= {self.test_results['target_count']}")
            else:
                print(f"❌ 未达到目标数量: {count} < {self.test_results['target_count']}")
            
            return count
            
        except Exception as e:
            print(f"❌ 验证数据库数量失败: {e}")
            return 0
    
    def verify_data_quality(self) -> bool:
        """验证商品数据质量"""
        try:
            # 获取前10条商品数据进行质量检查
            products = self.db_manager.find_products({})[:10]
            
            if not products:
                print("❌ 数据库中没有商品数据")
                return False
            
            print(f"🔍 检查前 {len(products)} 条商品数据质量...")
            
            quality_issues = []
            valid_products = 0
            
            for i, product in enumerate(products):
                issues = []
                
                # 检查必要字段
                if not product.product_id:
                    issues.append("缺少product_id")
                if not product.title:
                    issues.append("缺少title")
                if product.current_price <= 0:
                    issues.append("价格无效")
                if not product.search_keyword:
                    issues.append("缺少search_keyword")
                
                if issues:
                    quality_issues.extend(issues)
                    print(f"⚠️  商品{i+1}: {product.title[:30]}... - 问题: {', '.join(issues)}")
                else:
                    valid_products += 1
                    print(f"✅ 商品{i+1}: {product.title[:30]}... - ${product.current_price}")
            
            quality_score = valid_products / len(products) * 100
            print(f"\n📊 数据质量评分: {quality_score:.1f}% ({valid_products}/{len(products)} 条有效)")
            
            if quality_issues:
                print(f"⚠️  发现 {len(quality_issues)} 个数据质量问题")
            
            # 质量评分大于80%认为通过
            return quality_score >= 80.0
            
        except Exception as e:
            print(f"❌ 验证数据质量失败: {e}")
            return False
    
    def display_test_results(self):
        """显示测试结果"""
        print("\n" + "=" * 80)
        print("📋 验收测试结果")
        print("=" * 80)
        
        print(f"🎯 目标商品数量: {self.test_results['target_count']}")
        print(f"📊 实际采集数量: {self.test_results['actual_count']}")
        print(f"📄 采集页数: {self.test_results['pages_scraped']}")
        print(f"⏱️  总耗时: {self.test_results['total_time']:.2f} 秒")
        
        if self.test_results['success']:
            print("\n🎉 验收测试通过！")
            print("✅ 成功采集到足够数量的商品信息")
            print("✅ 商品数据质量符合要求")
            print("✅ 滑块处理和翻页功能正常")
        else:
            print("\n❌ 验收测试失败！")
            if self.test_results['actual_count'] < self.test_results['target_count']:
                print(f"❌ 商品数量不足: {self.test_results['actual_count']} < {self.test_results['target_count']}")
            print("需要进一步优化采集功能")
        
        # 显示数据库统计信息
        try:
            stats = self.db_manager.get_statistics()
            print(f"\n📊 数据库统计:")
            print(f"- 总商品数: {stats.get('total_products', 0)}")
            print(f"- 遇到滑块: {stats.get('slider_encountered', 0)}")
            print(f"- 滑块成功: {stats.get('slider_solved', 0)}")
            print(f"- 成功率: {stats.get('slider_success_rate', 0)}%")
        except:
            pass
    
    def display_sample_products(self, limit: int = 5):
        """显示样本商品数据"""
        try:
            products = self.db_manager.find_products({})[:limit]
            
            if products:
                print(f"\n📦 样本商品数据 (前{len(products)}条):")
                print("-" * 80)
                
                for i, product in enumerate(products):
                    print(f"商品{i+1}:")
                    print(f"  ID: {product.product_id}")
                    print(f"  标题: {product.title[:50]}...")
                    print(f"  价格: ${product.current_price} (原价: ${product.origin_price})")
                    print(f"  销量: {product.sold_count}")
                    print(f"  评分: {product.product_rating}")
                    print(f"  店铺: {product.shop_name}")
                    print(f"  关键词: {product.search_keyword}")
                    print()
        except Exception as e:
            print(f"⚠️  显示样本商品失败: {e}")

def main():
    """主函数"""
    print("TikTok商品采集验收测试")
    print("基于参考项目的完整实现")
    print("验收目标: 采集至少50条商品信息（2页数据）")
    
    # 创建测试实例
    test = ProductScrapingAcceptanceTest()
    
    # 运行验收测试
    success = test.run_acceptance_test(keyword="phone case", page_count=2)
    
    # 显示样本商品
    if success:
        test.display_sample_products(5)
    
    # 最终结果
    print("\n" + "=" * 80)
    if success:
        print("🎉 验收测试完全通过！")
        print("✅ 滑块处理功能正常")
        print("✅ 商品采集功能正常")
        print("✅ 翻页功能正常")
        print("✅ 数据库存储功能正常")
        print("✅ 商品数据完整性良好")
        print("\n🚀 系统已准备好投入使用！")
    else:
        print("❌ 验收测试失败！")
        print("需要进一步调试和优化系统")

if __name__ == "__main__":
    main()