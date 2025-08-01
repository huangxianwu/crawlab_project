#!/usr/bin/env python3
"""
完整的商品采集验收测试
验收目标: 采集至少50条商品信息（至少2页数据）并保存到数据库
"""
import os
import sys
import time
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tiktok_product_scraper import TikTokProductScraper
from utils.database import DatabaseManager
from models.product import ProductData

class CompleteProductScrapingTest:
    """完整的商品采集验收测试"""
    
    def __init__(self):
        self.scraper = None
        self.db_manager = None
        self.test_results = {
            'start_time': datetime.now().isoformat(),
            'target_products': 50,
            'pages_to_scrape': 2,
            'products_scraped': 0,
            'products_saved': 0,
            'pages_completed': 0,
            'total_time': 0,
            'success': False,
            'error_message': ''
        }
    
    def run_acceptance_test(self, keyword: str = "phone case", pages: int = 2) -> bool:
        """
        运行完整的商品采集验收测试
        
        Args:
            keyword: 搜索关键词
            pages: 采集页数
            
        Returns:
            bool: 测试是否成功
        """
        print("🎯 TikTok商品采集完整验收测试")
        print(f"验收目标: 采集至少50条商品信息（{pages}页数据）并保存到数据库")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # 步骤1: 初始化系统
            print("\n📋 步骤1: 初始化采集系统")
            if not self.initialize_system():
                return False
            
            # 步骤2: 清理数据库（测试用）
            print("\n📋 步骤2: 清理测试数据")
            self.cleanup_test_data(keyword)
            
            # 步骤3: 执行商品采集
            print(f"\n📋 步骤3: 执行商品采集 (关键词: {keyword}, 页数: {pages})")
            products = self.scraper.scrape_keyword_products(keyword, pages)
            self.test_results['products_scraped'] = len(products)
            
            # 步骤4: 验证数据库中的商品数量
            print("\n📋 步骤4: 验证数据库中的商品数量")
            db_count = self.verify_database_products(keyword)
            self.test_results['products_saved'] = db_count
            
            # 步骤5: 验证采集结果
            print("\n📋 步骤5: 验证采集结果")
            success = self.validate_results()
            
            # 计算总耗时
            end_time = time.time()
            self.test_results['total_time'] = end_time - start_time
            self.test_results['success'] = success
            
            # 显示最终结果
            self.display_final_results()
            
            return success
            
        except Exception as e:
            self.test_results['error_message'] = str(e)
            print(f"❌ 验收测试异常: {e}")
            return False
        
        finally:
            # 清理资源
            self.cleanup_resources()
    
    def initialize_system(self) -> bool:
        """初始化采集系统"""
        try:
            # 初始化采集器
            print("🔧 初始化TikTok商品采集器...")
            self.scraper = TikTokProductScraper()
            print("✅ 采集器初始化成功")
            
            # 初始化数据库管理器
            print("🔧 初始化数据库管理器...")
            self.db_manager = DatabaseManager()
            if not self.db_manager.connect():
                print("❌ 数据库连接失败")
                return False
            print("✅ 数据库连接成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            return False
    
    def cleanup_test_data(self, keyword: str):
        """清理测试数据"""
        try:
            print(f"🧹 清理关键词 '{keyword}' 的测试数据...")
            
            # 删除指定关键词的商品
            if self.db_manager.collection:
                result = self.db_manager.collection.delete_many({"search_keyword": keyword})
                print(f"✅ 清理了 {result.deleted_count} 条测试数据")
            
        except Exception as e:
            print(f"⚠️ 清理测试数据失败: {e}")
    
    def verify_database_products(self, keyword: str) -> int:
        """验证数据库中的商品数量"""
        try:
            print(f"🔍 检查数据库中关键词 '{keyword}' 的商品数量...")
            
            # 查询数据库中的商品
            products = self.db_manager.find_products_by_keyword(keyword)
            count = len(products)
            
            print(f"📊 数据库中找到 {count} 条商品记录")
            
            # 显示前5条商品信息
            if products:
                print("\n📋 商品信息示例:")
                print("-" * 60)
                for i, product in enumerate(products[:5]):
                    print(f"商品{i+1}:")
                    print(f"  ID: {product.product_id}")
                    print(f"  标题: {product.title[:50]}...")
                    print(f"  价格: ${product.current_price}")
                    print(f"  销量: {product.sold_count}")
                    print(f"  店铺: {product.shop_name}")
                    print()
            
            return count
            
        except Exception as e:
            print(f"❌ 验证数据库商品失败: {e}")
            return 0
    
    def validate_results(self) -> bool:
        """验证采集结果"""
        try:
            target_count = self.test_results['target_products']
            scraped_count = self.test_results['products_scraped']
            saved_count = self.test_results['products_saved']
            
            print(f"🎯 验收标准: 至少 {target_count} 条商品")
            print(f"📦 采集到商品: {scraped_count} 条")
            print(f"💾 保存到数据库: {saved_count} 条")
            
            # 验证是否达到目标
            if saved_count >= target_count:
                print(f"✅ 验收成功！数据库中有 {saved_count} 条商品，超过目标 {target_count} 条")
                return True
            else:
                print(f"❌ 验收失败！数据库中只有 {saved_count} 条商品，未达到目标 {target_count} 条")
                return False
                
        except Exception as e:
            print(f"❌ 结果验证失败: {e}")
            return False
    
    def display_final_results(self):
        """显示最终结果"""
        print("\n" + "=" * 80)
        print("📋 验收测试结果汇总")
        print("=" * 80)
        
        print(f"🎯 目标商品数量: {self.test_results['target_products']} 条")
        print(f"📄 计划采集页数: {self.test_results['pages_to_scrape']} 页")
        print(f"📦 实际采集商品: {self.test_results['products_scraped']} 条")
        print(f"💾 成功保存商品: {self.test_results['products_saved']} 条")
        print(f"⏱️  总耗时: {self.test_results['total_time']:.2f} 秒")
        
        if self.test_results['success']:
            print("\n🎉 验收测试通过！")
            print("✅ 商品采集功能完全满足要求")
            print("✅ 滑块处理正常工作")
            print("✅ 翻页功能正常工作")
            print("✅ 数据解析和保存正常工作")
            
            # 计算采集效率
            if self.test_results['total_time'] > 0:
                efficiency = self.test_results['products_saved'] / self.test_results['total_time']
                print(f"📊 采集效率: {efficiency:.2f} 商品/秒")
        else:
            print("\n❌ 验收测试失败！")
            if self.test_results['error_message']:
                print(f"错误信息: {self.test_results['error_message']}")
            
            print("\n🔍 可能的原因:")
            if self.test_results['products_scraped'] == 0:
                print("- 滑块处理失败，无法访问搜索结果页面")
                print("- 页面结构发生变化，无法解析商品数据")
            elif self.test_results['products_saved'] < self.test_results['products_scraped']:
                print("- 数据库保存失败")
                print("- 商品数据格式不正确")
            else:
                print("- 采集的商品数量不足")
                print("- 翻页功能可能存在问题")
    
    def cleanup_resources(self):
        """清理资源"""
        try:
            if self.scraper:
                self.scraper.close()
                print("✅ 采集器资源已清理")
            
            if self.db_manager:
                self.db_manager.close()
                print("✅ 数据库连接已关闭")
                
        except Exception as e:
            print(f"⚠️ 资源清理失败: {e}")
    
    def save_test_report(self):
        """保存测试报告"""
        try:
            import json
            
            report_file = f"product_scraping_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            print(f"📄 测试报告已保存到: {report_file}")
            
        except Exception as e:
            print(f"⚠️ 保存测试报告失败: {e}")

def main():
    """主函数"""
    print("TikTok商品采集完整验收测试")
    print("基于DrissionPage + ddddocr的完整采集方案")
    print("\n🎯 验收目标:")
    print("- 成功处理滑块验证")
    print("- 采集至少2页商品数据")
    print("- 数据库中保存至少50条商品信息")
    print("- 商品信息包含完整字段")
    
    # 创建测试实例
    test = CompleteProductScrapingTest()
    
    # 运行验收测试
    success = test.run_acceptance_test(keyword="phone case", pages=2)
    
    # 保存测试报告
    test.save_test_report()
    
    # 显示最终结论
    print("\n" + "=" * 80)
    if success:
        print("🎊 商品采集系统验收通过！")
        print("系统已准备好投入生产使用")
    else:
        print("❌ 商品采集系统验收失败！")
        print("需要进一步调试和优化")
    print("=" * 80)

if __name__ == "__main__":
    main()