#!/usr/bin/env python3
"""
简化版Crawlab爬虫运行器
避免复杂的模块依赖，直接内联所有必要的功能
"""
import sys
import os
import time
import json
import logging
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional

# 基础配置
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "crawler_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "products")

# 设置基础日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('crawlab_crawler')

def log_debug_info():
    """输出调试信息"""
    print("=" * 60)
    print("🔍 [DEBUG] Crawlab简化爬虫调试信息")
    print("=" * 60)
    print(f"[DEBUG] Python版本: {sys.version}")
    print(f"[DEBUG] 脚本文件: {__file__}")
    print(f"[DEBUG] 当前工作目录: {os.getcwd()}")
    print(f"[DEBUG] 环境变量:")
    print(f"  MONGO_URI: {MONGO_URI}")
    print(f"  DATABASE_NAME: {DATABASE_NAME}")
    print(f"  COLLECTION_NAME: {COLLECTION_NAME}")
    
    # 检查关键文件
    key_files = ['config.py', 'requirements.txt']
    for file in key_files:
        exists = os.path.exists(file)
        print(f"  {file}: {'存在' if exists else '不存在'}")
    
    print("=" * 60)

class SimpleCrawlabCrawler:
    """简化的Crawlab爬虫"""
    
    def __init__(self):
        self.logger = logger
        self.mongo_client = None
        self.db = None
        self.collection = None
        self.page = None
        self.det = None
        
        print("🚀 初始化简化版Crawlab爬虫...")
        self.logger.info("简化版Crawlab爬虫初始化")
    
    def setup_dependencies(self):
        """设置依赖"""
        try:
            # 尝试导入必要的依赖
            global ChromiumPage, ChromiumOptions, ddddocr, pymongo
            
            from DrissionPage import ChromiumPage, ChromiumOptions
            import ddddocr
            import pymongo
            
            print("✅ 所有依赖导入成功")
            self.logger.info("依赖导入成功")
            return True
            
        except ImportError as e:
            print(f"❌ 依赖导入失败: {e}")
            self.logger.error(f"依赖导入失败: {e}")
            return False
    
    def setup_database(self):
        """设置数据库连接"""
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # 测试连接
            self.mongo_client.admin.command('ping')
            
            self.db = self.mongo_client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            print(f"✅ 数据库连接成功: {DATABASE_NAME}.{COLLECTION_NAME}")
            self.logger.info(f"数据库连接成功: {DATABASE_NAME}.{COLLECTION_NAME}")
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            self.logger.error(f"数据库连接失败: {e}")
            return False
    
    def setup_browser(self):
        """设置浏览器"""
        try:
            # 配置浏览器选项
            options = ChromiumOptions()
            options.headless(True)  # Crawlab环境使用无头模式
            options.set_argument('--no-sandbox')
            options.set_argument('--disable-dev-shm-usage')
            options.set_argument('--disable-gpu')
            options.set_argument('--window-size=1920,1080')
            
            # 创建页面对象
            self.page = ChromiumPage(addr_or_opts=options)
            
            print("✅ 浏览器初始化成功")
            self.logger.info("浏览器初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ 浏览器初始化失败: {e}")
            self.logger.error(f"浏览器初始化失败: {e}")
            return False
    
    def setup_captcha_solver(self):
        """设置验证码识别"""
        try:
            self.det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
            print("✅ 验证码识别器初始化成功")
            self.logger.info("验证码识别器初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ 验证码识别器初始化失败: {e}")
            self.logger.error(f"验证码识别器初始化失败: {e}")
            return False
    
    def crawl_keyword(self, keyword: str, max_pages: int = 1) -> int:
        """
        爬取指定关键词的商品数据
        
        Args:
            keyword: 搜索关键词
            max_pages: 最大页数
            
        Returns:
            int: 采集到的商品数量
        """
        print(f"🎯 开始采集关键词: {keyword}")
        self.logger.info(f"开始采集关键词: {keyword}")
        
        try:
            # 构建搜索URL
            encoded_keyword = urllib.parse.quote(keyword)
            search_url = f"https://www.tiktok.com/shop/s/{encoded_keyword}"
            
            print(f"🌐 访问搜索页面: {search_url}")
            self.page.get(search_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 检查是否有验证码
            if self.detect_captcha():
                print("🧩 检测到验证码，尝试处理...")
                if not self.handle_captcha():
                    print("❌ 验证码处理失败")
                    return 0
                print("✅ 验证码处理成功")
            
            # 提取商品数据
            products_count = self.extract_products(keyword)
            
            print(f"✅ 关键词 '{keyword}' 采集完成，共采集 {products_count} 个商品")
            self.logger.info(f"关键词采集完成: {keyword}, 数量: {products_count}")
            
            return products_count
            
        except Exception as e:
            print(f"❌ 采集关键词失败: {keyword} - {e}")
            self.logger.error(f"采集关键词失败: {keyword} - {e}")
            return 0
    
    def detect_captcha(self) -> bool:
        """检测是否有验证码"""
        try:
            # 检查页面标题
            title = self.page.title
            if "Security Check" in title:
                return True
            
            # 检查是否有验证码元素
            captcha_elements = self.page.eles('tag:img')
            return len(captcha_elements) >= 2
            
        except Exception as e:
            self.logger.warning(f"验证码检测失败: {e}")
            return False
    
    def handle_captcha(self) -> bool:
        """处理验证码"""
        try:
            # 查找验证码图片
            images = self.page.eles('tag:img')
            if len(images) < 2:
                return False
            
            # 获取背景图和滑块图
            bg_img = images[0]
            slider_img = images[1]
            
            # 下载图片
            bg_url = bg_img.attr('src')
            slider_url = slider_img.attr('src')
            
            if not bg_url or not slider_url:
                return False
            
            # 使用ddddocr识别滑块位置
            import requests
            bg_response = requests.get(bg_url)
            slider_response = requests.get(slider_url)
            
            if bg_response.status_code == 200 and slider_response.status_code == 200:
                target_x = self.det.slide_match(bg_response.content, slider_response.content)
                print(f"🎯 识别到滑块位置: {target_x}")
                
                # 查找滑块元素并拖拽
                slider_element = self.page.ele('css:[class*="slider"]')
                if slider_element:
                    # 计算实际拖拽距离
                    actual_distance = target_x * 0.6  # 根据页面缩放调整
                    
                    # 执行拖拽
                    slider_element.drag((actual_distance, 0), duration=0.2)
                    time.sleep(2)
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"验证码处理失败: {e}")
            return False
    
    def extract_products(self, keyword: str) -> int:
        """提取商品数据"""
        try:
            # 查找页面数据脚本
            script_elements = self.page.eles('tag:script')
            
            for script in script_elements:
                script_content = script.inner_html
                if 'window.__UNIVERSAL_DATA_FOR_REHYDRATION__' in script_content:
                    # 解析页面数据
                    start_idx = script_content.find('{')
                    end_idx = script_content.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != -1:
                        json_str = script_content[start_idx:end_idx]
                        data = json.loads(json_str)
                        
                        # 提取商品信息
                        products_count = self.parse_products_from_data(data, keyword)
                        return products_count
            
            return 0
            
        except Exception as e:
            self.logger.error(f"提取商品数据失败: {e}")
            return 0
    
    def parse_products_from_data(self, data: dict, keyword: str) -> int:
        """从页面数据中解析商品"""
        try:
            products_count = 0
            
            # 遍历数据结构查找商品
            def find_products(obj, path=""):
                nonlocal products_count
                
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == "products" and isinstance(value, list):
                            # 找到商品列表
                            for product in value:
                                if self.save_product(product, keyword):
                                    products_count += 1
                        else:
                            find_products(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        find_products(item, f"{path}[{i}]")
            
            find_products(data)
            return products_count
            
        except Exception as e:
            self.logger.error(f"解析商品数据失败: {e}")
            return 0
    
    def save_product(self, product: dict, keyword: str) -> bool:
        """保存商品到数据库"""
        try:
            # 提取商品基本信息
            product_id = product.get("product_id", "")
            title = product.get("title", "")
            
            if not product_id or not title:
                return False
            
            # 构建商品数据
            product_data = {
                "product_id": product_id,
                "title": title,
                "keyword": keyword,
                "scraped_at": datetime.now(),
                "slider_encountered": True,
                "slider_solved": True,
                "source": "tiktok_shop"
            }
            
            # 保存到数据库
            self.collection.insert_one(product_data)
            print(f"💾 保存商品: {title[:50]}...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"保存商品失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.page:
                self.page.quit()
                print("✅ 浏览器已关闭")
            
            if self.mongo_client:
                self.mongo_client.close()
                print("✅ 数据库连接已关闭")
                
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")
    
    def run(self, keywords: str = "phone case", max_pages: int = 1):
        """
        运行爬虫
        
        Args:
            keywords: 关键词（逗号分隔）
            max_pages: 最大页数
        """
        print("🎉 Crawlab简化爬虫开始运行")
        print("=" * 60)
        
        # 初始化各个组件
        if not self.setup_dependencies():
            return
        
        if not self.setup_database():
            return
        
        if not self.setup_browser():
            return
        
        if not self.setup_captcha_solver():
            return
        
        try:
            # 处理关键词列表
            keyword_list = [k.strip() for k in keywords.split(',')]
            total_products = 0
            
            for keyword in keyword_list:
                if keyword:
                    count = self.crawl_keyword(keyword, max_pages)
                    total_products += count
                    
                    # 关键词间隔
                    time.sleep(2)
            
            print("=" * 60)
            print(f"🎊 爬虫运行完成！")
            print(f"✅ 处理关键词: {len(keyword_list)} 个")
            print(f"✅ 采集商品: {total_products} 个")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ 爬虫运行失败: {e}")
            self.logger.error(f"爬虫运行失败: {e}")
        
        finally:
            self.cleanup()


def main():
    """主函数"""
    # 输出调试信息
    log_debug_info()
    
    # 获取参数
    keywords = os.getenv("keywords", "phone case")
    max_pages = int(os.getenv("max_pages", "1"))
    
    print(f"📋 运行参数:")
    print(f"  关键词: {keywords}")
    print(f"  最大页数: {max_pages}")
    print()
    
    # 创建并运行爬虫
    crawler = SimpleCrawlabCrawler()
    crawler.run(keywords, max_pages)


if __name__ == "__main__":
    main()