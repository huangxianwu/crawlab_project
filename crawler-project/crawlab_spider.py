#!/usr/bin/env python3
"""
Crawlab电商爬虫脚本
集成到Crawlab平台的主要爬虫脚本
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import List, Dict, Any

# 路径修复 - 确保能找到项目模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import Config
from utils.logger import setup_logger, get_logger
from utils.webdriver import WebDriverManager
from handlers.extractor import DataExtractor
from handlers.slider import SliderHandler
from models.product import ProductData
from utils.database import get_db_manager


class CrawlabSpider:
    """Crawlab电商爬虫类"""
    
    def __init__(self):
        """初始化爬虫"""
        self.logger = setup_logger('crawlab_spider')
        self.webdriver_manager = None
        self.db_manager = get_db_manager()
        self.stats = {
            'total_keywords': 0,
            'total_products': 0,
            'successful_keywords': 0,
            'failed_keywords': 0,
            'slider_encountered': 0,
            'slider_solved': 0,
            'start_time': None,
            'end_time': None
        }
        
        self.logger.info("Crawlab电商爬虫初始化完成")
    
    def parse_arguments(self):
        """解析命令行参数"""
        parser = argparse.ArgumentParser(description='Crawlab电商爬虫')
        parser.add_argument('--keywords', type=str, help='搜索关键词，多个关键词用逗号分隔')
        parser.add_argument('--max-pages', type=int, default=1, help='每个关键词最大采集页数')
        parser.add_argument('--headless', action='store_true', help='使用无头模式')
        parser.add_argument('--output', type=str, help='输出文件路径')
        
        args = parser.parse_args()
        
        # 如果没有提供关键词，尝试从环境变量获取
        if not args.keywords:
            args.keywords = os.getenv('CRAWLAB_KEYWORDS', 'phone case,wireless charger')
        
        return args
    
    def setup_crawlab_environment(self):
        """设置Crawlab环境"""
        try:
            # 检查是否在Crawlab环境中运行
            crawlab_task_id = os.getenv('CRAWLAB_TASK_ID')
            crawlab_node_id = os.getenv('CRAWLAB_NODE_ID')
            
            if crawlab_task_id:
                self.logger.info(f"运行在Crawlab环境中")
                self.logger.info(f"任务ID: {crawlab_task_id}")
                self.logger.info(f"节点ID: {crawlab_node_id}")
                
                # 设置Crawlab特定的配置
                self.is_crawlab_env = True
            else:
                self.logger.info("运行在本地环境中")
                self.is_crawlab_env = False
                
        except Exception as e:
            self.logger.error(f"设置Crawlab环境失败: {e}")
            self.is_crawlab_env = False
    
    def crawl_keyword(self, keyword: str, max_pages: int = 1) -> List[ProductData]:
        """爬取单个关键词的商品数据"""
        products = []
        
        try:
            self.logger.info(f"开始爬取关键词: {keyword}")
            
            # 创建WebDriver
            if not self.webdriver_manager:
                self.webdriver_manager = WebDriverManager(headless=True)
                driver = self.webdriver_manager.create_driver()
                
                if not driver:
                    raise Exception("WebDriver创建失败")
            
            # 搜索关键词
            if self.webdriver_manager.search_products(keyword):
                self.logger.info(f"成功搜索关键词: {keyword}")
                
                # 检测和处理滑块
                slider_handler = SliderHandler(self.webdriver_manager.get_driver())
                
                if slider_handler.detect_slider():
                    self.stats['slider_encountered'] += 1
                    self.logger.warning("检测到滑块验证")
                    
                    if slider_handler.handle_captcha_with_retry():
                        self.stats['slider_solved'] += 1
                        self.logger.info("滑块验证处理成功")
                    else:
                        self.logger.error("滑块验证处理失败，跳过此关键词")
                        self.stats['failed_keywords'] += 1
                        return products
                
                # 提取商品数据
                for page_num in range(1, max_pages + 1):
                    self.logger.info(f"提取第 {page_num} 页数据")
                    
                    page_products_data = self.webdriver_manager.extract_products_from_page(keyword, page_num)
                    
                    for product_data in page_products_data:
                        try:
                            product = ProductData(
                                keyword=keyword,
                                title=product_data.get('title', ''),
                                scraped_at=datetime.now(),
                                slider_encountered=self.stats['slider_encountered'] > 0,
                                slider_solved=self.stats['slider_solved'] > 0
                            )
                            products.append(product)
                        except Exception as e:
                            self.logger.warning(f"创建商品对象失败: {e}")
                    
                    # 翻页延时
                    if page_num < max_pages:
                        time.sleep(2)
                
                self.stats['successful_keywords'] += 1
                self.logger.info(f"关键词 '{keyword}' 爬取完成，获得 {len(products)} 个商品")
                
            else:
                self.logger.error(f"搜索关键词 '{keyword}' 失败")
                self.stats['failed_keywords'] += 1
                
        except Exception as e:
            self.logger.error(f"爬取关键词 '{keyword}' 时发生错误: {e}")
            self.stats['failed_keywords'] += 1
        
        return products
    
    def save_products_to_database(self, products: List[ProductData]) -> int:
        """保存商品数据到数据库"""
        saved_count = 0
        
        try:
            if self.db_manager.connect():
                for product in products:
                    if self.db_manager.insert_product(product):
                        saved_count += 1
                        
                        # 在Crawlab环境中输出结果
                        if self.is_crawlab_env:
                            # Crawlab会自动收集这种格式的输出
                            result_data = {
                                'keyword': product.keyword,
                                'title': product.title,
                                'scraped_at': product.scraped_at.isoformat(),
                                'slider_encountered': product.slider_encountered,
                                'slider_solved': product.slider_solved
                            }
                            print(json.dumps(result_data, ensure_ascii=False))
                
                self.db_manager.disconnect()
                self.logger.info(f"成功保存 {saved_count} 个商品到数据库")
            else:
                self.logger.error("数据库连接失败")
                
        except Exception as e:
            self.logger.error(f"保存数据到数据库失败: {e}")
        
        return saved_count
    
    def save_products_to_file(self, products: List[ProductData], output_file: str):
        """保存商品数据到文件"""
        try:
            products_data = []
            for product in products:
                products_data.append({
                    'keyword': product.keyword,
                    'title': product.title,
                    'scraped_at': product.scraped_at.isoformat(),
                    'slider_encountered': product.slider_encountered,
                    'slider_solved': product.slider_solved
                })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"商品数据已保存到文件: {output_file}")
            
        except Exception as e:
            self.logger.error(f"保存数据到文件失败: {e}")
    
    def print_statistics(self):
        """打印统计信息"""
        self.stats['end_time'] = datetime.now()
        
        if self.stats['start_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            duration_str = str(duration).split('.')[0]  # 去掉微秒
        else:
            duration_str = "未知"
        
        print("\n" + "=" * 60)
        print("📊 爬取统计信息")
        print("=" * 60)
        print(f"总关键词数: {self.stats['total_keywords']}")
        print(f"成功关键词: {self.stats['successful_keywords']}")
        print(f"失败关键词: {self.stats['failed_keywords']}")
        print(f"总商品数: {self.stats['total_products']}")
        print(f"遇到滑块: {self.stats['slider_encountered']} 次")
        print(f"滑块成功: {self.stats['slider_solved']} 次")
        
        if self.stats['slider_encountered'] > 0:
            success_rate = (self.stats['slider_solved'] / self.stats['slider_encountered']) * 100
            print(f"滑块成功率: {success_rate:.1f}%")
        
        print(f"执行时间: {duration_str}")
        print("=" * 60)
        
        # 记录到日志
        self.logger.info(f"爬取完成统计: 关键词{self.stats['successful_keywords']}/{self.stats['total_keywords']}, "
                        f"商品{self.stats['total_products']}个, 耗时{duration_str}")
    
    def run(self):
        """运行爬虫"""
        try:
            self.stats['start_time'] = datetime.now()
            
            # 解析参数
            args = self.parse_arguments()
            
            # 设置Crawlab环境
            self.setup_crawlab_environment()
            
            # 解析关键词
            keywords = [kw.strip() for kw in args.keywords.split(',') if kw.strip()]
            self.stats['total_keywords'] = len(keywords)
            
            self.logger.info(f"开始爬取任务，关键词: {keywords}")
            self.logger.info(f"最大页数: {args.max_pages}")
            self.logger.info(f"无头模式: {args.headless}")
            
            all_products = []
            
            # 逐个处理关键词
            for i, keyword in enumerate(keywords, 1):
                self.logger.info(f"处理关键词 {i}/{len(keywords)}: {keyword}")
                
                products = self.crawl_keyword(keyword, args.max_pages)
                all_products.extend(products)
                
                # 关键词间延时
                if i < len(keywords):
                    delay = 3
                    self.logger.info(f"关键词间延时 {delay} 秒...")
                    time.sleep(delay)
            
            self.stats['total_products'] = len(all_products)
            
            # 保存数据
            if all_products:
                # 保存到数据库
                saved_count = self.save_products_to_database(all_products)
                self.logger.info(f"数据库保存: {saved_count}/{len(all_products)}")
                
                # 保存到文件（如果指定了输出文件）
                if args.output:
                    self.save_products_to_file(all_products, args.output)
            
            # 打印统计信息
            self.print_statistics()
            
            self.logger.info("爬取任务完成")
            
        except Exception as e:
            self.logger.error(f"爬取任务执行失败: {e}")
            raise
        
        finally:
            # 清理资源
            if self.webdriver_manager:
                self.webdriver_manager.close_driver()
                self.logger.info("WebDriver资源已清理")


def main():
    """主函数"""
    try:
        spider = CrawlabSpider()
        spider.run()
        
    except KeyboardInterrupt:
        print("\n用户中断爬取任务")
        
    except Exception as e:
        print(f"爬取任务失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()