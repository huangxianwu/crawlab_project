#!/usr/bin/env python3
"""
增强字段验证测试
验证新增字段的采集和存储功能
"""
import os
import sys
import time
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'demo'))

from reference_based_scraper import ReferenceBasedScraper
from utils.database import DatabaseManager

class EnhancedFieldsVerificationTest:
    """增强字段验证测试"""
    
    def __init__(self):
        self.scraper = None
        self.db_manager = DatabaseManager()
        self.test_results = {
            'start_time': datetime.now().isoformat(),
            'products_scraped': 0,
            'fields_verified': {},
            'success': False
        }
    
    def run_verification_test(self, keyword: str = "phone case", page_count: int = 1) -> bool:
        """
        运行增强字段验证测试
        
        Args:
            keyword: 搜索关键词
            page_count: 采集页数
            
        Returns:
            bool: 测试是否通过
        """
        print("🔍 增强字段验证测试")
        print("验证目标: 商品链接、评论时间等字段的采集和存储")
        print("=" * 80)
        
        try:
            # 步骤1: 准备数据库
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
            self.test_results['products_scraped'] = len(scraped_products)
            
            # 步骤4: 验证字段完整性
            print(f"\n📋 步骤4: 验证字段完整性")
            fields_verified = self.verify_enhanced_fields()
            self.test_results['fields_verified'] = fields_verified
            
            # 步骤5: 显示验证结果
            self.display_verification_results()
            
            # 判断测试结果
            success = all(fields_verified.values())
            self.test_results['success'] = success
            
            return success
            
        except Exception as e:
            print(f"❌ 验证测试异常: {e}")
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
            
            # 清空数据库以便测试
            if self.db_manager.clear_collection():
                print("✅ 数据库已清空")
            else:
                print("⚠️  数据库清空失败，继续测试")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据库准备失败: {e}")
            return False
    
    def verify_enhanced_fields(self) -> dict:
        """验证增强字段"""
        try:
            # 获取数据库中的商品
            products = self.db_manager.find_products({})[:10]
            
            if not products:
                print("❌ 数据库中没有商品数据")
                return {}
            
            print(f"🔍 检查前 {len(products)} 条商品的字段完整性...")
            
            fields_status = {
                'product_url': {'found': 0, 'missing': 0, 'examples': []},
                'latest_review_fmt': {'found': 0, 'missing': 0, 'examples': []},
                'earliest_review_fmt': {'found': 0, 'missing': 0, 'examples': []},
                'shop_name': {'found': 0, 'missing': 0, 'examples': []}
            }
            
            for i, product in enumerate(products):
                print(f"\n商品{i+1}: {product.title[:40]}...")
                
                # 检查商品链接
                if hasattr(product, 'product_url') and product.product_url:
                    fields_status['product_url']['found'] += 1
                    fields_status['product_url']['examples'].append(product.product_url)
                    print(f"  ✅ 商品链接: {product.product_url}")
                else:
                    fields_status['product_url']['missing'] += 1
                    print(f"  ❌ 商品链接: 缺失")
                
                # 检查最近评价时间
                if product.latest_review_fmt:
                    fields_status['latest_review_fmt']['found'] += 1
                    fields_status['latest_review_fmt']['examples'].append(product.latest_review_fmt)
                    print(f"  ✅ 最近评价时间: {product.latest_review_fmt}")
                else:
                    fields_status['latest_review_fmt']['missing'] += 1
                    print(f"  ❌ 最近评价时间: 缺失")
                
                # 检查最早评价时间
                if product.earliest_review_fmt:
                    fields_status['earliest_review_fmt']['found'] += 1
                    fields_status['earliest_review_fmt']['examples'].append(product.earliest_review_fmt)
                    print(f"  ✅ 最早评价时间: {product.earliest_review_fmt}")
                else:
                    fields_status['earliest_review_fmt']['missing'] += 1
                    print(f"  ❌ 最早评价时间: 缺失")
                
                # 检查店铺名称
                if product.shop_name:
                    fields_status['shop_name']['found'] += 1
                    fields_status['shop_name']['examples'].append(product.shop_name)
                    print(f"  ✅ 店铺名称: {product.shop_name}")
                else:
                    fields_status['shop_name']['missing'] += 1
                    print(f"  ❌ 店铺名称: 缺失")
            
            # 计算字段完整性
            field_completeness = {}
            for field, status in fields_status.items():
                total = status['found'] + status['missing']
                if total > 0:
                    completeness = status['found'] / total * 100
                    field_completeness[field] = completeness >= 80.0  # 80%以上认为通过
                else:
                    field_completeness[field] = False
            
            return field_completeness
            
        except Exception as e:
            print(f"❌ 验证增强字段失败: {e}")
            return {}
    
    def display_verification_results(self):
        """显示验证结果"""
        print("\n" + "=" * 80)
        print("📋 增强字段验证结果")
        print("=" * 80)
        
        print(f"📊 采集商品数量: {self.test_results['products_scraped']}")
        
        if self.test_results['fields_verified']:
            print("\n🔍 字段完整性检查:")
            for field, is_complete in self.test_results['fields_verified'].items():
                status = "✅ 通过" if is_complete else "❌ 失败"
                print(f"  {field}: {status}")
        
        if self.test_results['success']:
            print("\n🎉 增强字段验证测试通过！")
            print("✅ 所有必需字段都已正确采集和存储")
            print("✅ 商品链接字段已添加")
            print("✅ 评论时间字段已采集")
            print("✅ 店铺名称字段已采集")
        else:
            print("\n❌ 增强字段验证测试失败！")
            print("需要进一步优化字段采集逻辑")

def main():
    """主函数"""
    print("TikTok商品增强字段验证测试")
    print("验证新增字段的采集和存储功能")
    
    # 创建测试实例
    test = EnhancedFieldsVerificationTest()
    
    # 运行验证测试
    success = test.run_verification_test(keyword="phone case", page_count=1)
    
    # 最终结果
    print("\n" + "=" * 80)
    if success:
        print("🎉 增强字段验证测试完全通过！")
        print("✅ 商品链接字段采集正常")
        print("✅ 评论时间字段采集正常")
        print("✅ 店铺名称字段采集正常")
        print("✅ 数据库存储功能正常")
        print("\n🚀 增强字段功能已准备就绪！")
    else:
        print("❌ 增强字段验证测试失败！")
        print("需要进一步调试和优化字段采集")

if __name__ == "__main__":
    main() 