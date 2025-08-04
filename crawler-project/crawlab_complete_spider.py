#!/usr/bin/env python3
"""
适用于Crawlab环境的完整TikTok Shop爬虫
包含完整的搜索、滑块处理、商品采集、保存功能
"""
import time
import json
import urllib.parse
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

# 确保项目路径在Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    import ddddocr
    import requests
    import cv2
    import numpy as np
    import pymongo
    DEPENDENCIES_OK = True
except ImportError as e:
    print(f"❌ 依赖导入失败: {e}")
    DEPENDENCIES_OK = False

class CrawlabTikTokSpider:
    """
    Crawlab环境下的TikTok Shop完整爬虫
    集成所有功能：搜索、滑块处理、商品采集、数据保存
    """
    
    def __init__(self):
        self.page = None
        self.det = None
        self.mongo_client = None
        self.db = None
        self.collection = None
        self.is_running = True
        
        # 配置信息
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "crawler_db")
        self.collection_name = os.getenv("COLLECTION_NAME", "products")
        
        print("🚀 Crawlab TikTok Shop爬虫初始化")
        print(f"📊 数据库配置: {self.mongo_uri}")
        
    def init_browser(self):
        """初始化浏览器"""
        try:
            print("🌐 正在启动Chrome浏览器...")
            co = ChromiumOptions()
            
            # 基础配置
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-dev-shm-usage')
            co.set_argument('--disable-gpu')
            co.set_argument('--disable-web-security')
            co.set_argument('--allow-running-insecure-content')
            
            # 创建页面实例
            self.page = ChromiumPage(co)
            self.page.set.user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0 Safari/537.36")
            self.page.set.load_mode.eager()
            
            print("✅ 浏览器初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 初始化浏览器失败: {e}")
            return False
    
    def init_ocr(self):
        """初始化OCR"""
        try:
            print("🔍 正在初始化验证码识别...")
            if DEPENDENCIES_OK:
                self.det = ddddocr.DdddOcr(det=False, ocr=False)
                print("✅ ddddocr滑块检测器初始化成功")
                return True
            else:
                print("❌ ddddocr依赖不可用")
                return False
                
        except Exception as e:
            print(f"❌ 初始化验证码识别失败: {e}")
            return False
    
    def init_database(self):
        """初始化数据库连接"""
        try:
            print("🔗 连接数据库...")
            self.mongo_client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.mongo_client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # 测试连接
            self.mongo_client.admin.command('ping')
            print("✅ 数据库连接成功")
            
            # 显示统计信息
            total_count = self.collection.count_documents({})
            print(f"📊 数据库中现有商品: {total_count} 条")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def navigate_to_url(self, url: str):
        """导航到指定URL"""
        try:
            print(f"🔄 访问页面: {url}")
            self.page.get(url)
            time.sleep(5)
            
            current_url = self.page.url
            current_title = self.page.title
            
            print(f"✅ 当前URL: {current_url}")
            print(f"✅ 页面标题: {current_title}")
            
            return current_url, current_title
            
        except Exception as e:
            print(f"❌ 页面导航失败: {e}")
            return None, None
    
    def handle_captcha(self) -> bool:
        """处理验证码"""
        try:
            html_text = self.page.html
            has_security_check = "Security Check" in self.page.title
            
            if not has_security_check:
                return False
            
            print("🔐 检测到验证码，正在处理...")
            
            # 查找验证码图片
            imgs = self.page.eles("tag=img", timeout=20)
            print(f"页面总共找到 {len(imgs)} 张图片")
            
            # 筛选显示的图片
            visible_imgs = []
            for i, img in enumerate(imgs):
                try:
                    if img.states.is_displayed:
                        src = img.attr("src") or ''
                        size = img.rect.size
                        if size[0] > 50 and size[1] > 50:
                            visible_imgs.append(img)
                except:
                    continue
            
            print(f"筛选出 {len(visible_imgs)} 张可见的验证码图片")
            
            if len(visible_imgs) < 2:
                print("⚠️ 验证码图片不足")
                return True
            
            # 获取验证码图片URL
            background_img_url = visible_imgs[0].attr("src")
            target_img_url = visible_imgs[1].attr("src")
            
            print(f"背景图URL: {background_img_url[:50]}...")
            print(f"滑块图URL: {target_img_url[:50]}...")
            
            # 下载验证码图片
            background_response = requests.get(background_img_url, timeout=10)
            target_response = requests.get(target_img_url, timeout=10)
            
            if background_response.status_code == 200 and target_response.status_code == 200:
                # 使用ddddocr的滑块匹配功能
                background_bytes = background_response.content
                target_bytes = target_response.content
                
                try:
                    res = self.det.slide_match(target_bytes, background_bytes)
                    if res and "target" in res:
                        target_x = res["target"][0]
                        print(f"🎯 识别到滑块位置: {target_x}")
                        
                        # 计算滑块位置的偏移量
                        x_offset = visible_imgs[1].rect.location[0] - visible_imgs[0].rect.location[0]
                        
                        # 获取图片尺寸进行缩放
                        img_array = np.frombuffer(background_bytes, dtype=np.uint8)
                        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        if img is not None:
                            height, width = img.shape[:2]
                            actual_x = target_x * (340 / width) - x_offset
                            print(f"📐 计算的实际滑动距离: {actual_x}")
                        else:
                            actual_x = target_x - x_offset
                        
                        # 执行滑动操作
                        slider_element = self.page.ele("xpath://*[@id='secsdk-captcha-drag-wrapper']/div[2]", timeout=5)
                        if slider_element:
                            print(f"✅ 找到滑块元素，开始拖拽")
                            slider_element.drag(actual_x, 10, 0.2)
                            time.sleep(3)
                            
                            # 检查验证码是否通过
                            new_html = self.page.html
                            if "captcha-verify-image" not in new_html:
                                print("✅ 验证码处理成功")
                                return False
                            else:
                                print("⚠️ 验证码未通过")
                        else:
                            print("⚠️ 未找到滑块元素")
                    else:
                        print("⚠️ 滑块位置识别失败")
                        
                except Exception as e:
                    print(f"⚠️ 滑块识别异常: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ 滑块处理异常: {e}")
            return True
    
    def get_components_map(self) -> List[Dict]:
        """获取页面组件映射"""
        try:
            ele = self.page.ele("@id=__MODERN_ROUTER_DATA__", timeout=10)
            if not ele:
                print("⚠️ 未找到页面数据元素")
                return []
            
            loader_data = json.loads(ele.inner_html)
            loader_keys = list(loader_data.get("loaderData", {}).keys())
            print(f"🔍 页面结构键: {loader_keys}")
            
            for key in loader_keys:
                if key and isinstance(loader_data["loaderData"][key], dict):
                    page_data = loader_data["loaderData"][key]
                    if "page_config" in page_data and "components_map" in page_data["page_config"]:
                        components_map = page_data["page_config"]["components_map"]
                        print(f"✅ 找到页面组件映射: {len(components_map)} 个组件")
                        return components_map
            
            print("⚠️ 未找到匹配的页面结构")
            return []
            
        except Exception as e:
            print(f"⚠️ 解析页面组件数据失败: {e}")
            return []
    
    def parse_product_data(self, product: Dict, keyword: str) -> Optional[Dict]:
        """解析商品数据"""
        try:
            product_id = product.get("product_id", "")
            title = product.get("title", "")
            
            # 价格信息
            price_info = product.get("product_price_info", {})
            current_price_str = price_info.get("sale_price_format", "0")
            origin_price_str = price_info.get("origin_price_format", current_price_str)
            
            try:
                current_price = float(current_price_str.replace('$', '').replace(',', ''))
                origin_price = float(origin_price_str.replace('$', '').replace(',', ''))
            except:
                current_price = 0.0
                origin_price = 0.0
            
            # 其他信息
            product_image = ""
            images = product.get("images", [])
            if images and len(images) > 0:
                product_image = images[0].get("url_list", [""])[0]
            
            sold_count = product.get("sold_count", 0)
            seller = product.get("seller", {})
            shop_name = seller.get("name", "")
            product_rating = product.get("product_rating", 0.0)
            review_count = product.get("review_count", 0)
            
            # 创建商品数据
            product_data = {
                'product_id': product_id,
                'title': title,
                'search_keyword': keyword,
                'current_price': current_price,
                'origin_price': origin_price,
                'shipping_fee': 0.0,
                'product_image': product_image,
                'product_url': f"https://www.tiktok.com/shop/product/{product_id}",
                'categories': "TikTok Shop",
                'desc_detail': "",
                'sold_count': sold_count,
                'product_rating': product_rating,
                'review_count': review_count,
                'review_count_str': str(review_count),
                'latest_review_fmt': "",
                'earliest_review_fmt': "",
                'shop_name': shop_name,
                'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'scraped_at': datetime.now().isoformat(),
                'slider_encountered': True,
                'slider_solved': True
            }
            
            return product_data
            
        except Exception as e:
            print(f"❌ 解析商品数据失败: {e}")
            return None
    
    def save_product_to_db(self, product_data: Dict):
        """保存商品到数据库"""
        try:
            # 检查是否已存在
            existing = self.collection.find_one({"product_id": product_data['product_id']})
            if existing:
                return False
            
            # 保存到数据库
            result = self.collection.insert_one(product_data)
            if result.inserted_id:
                print(f"💾 保存商品: {product_data['title'][:30]}... - ${product_data['current_price']}")
                
                # 输出Crawlab格式的结果
                crawlab_result = {
                    'product_id': product_data['product_id'],
                    'title': product_data['title'],
                    'price': product_data['current_price'],
                    'shop_name': product_data['shop_name'],
                    'scraped_at': product_data['scraped_at']
                }
                print(json.dumps(crawlab_result, ensure_ascii=False))
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ 保存商品到数据库失败: {e}")
            return False
    
    def scrape_keyword_products(self, keyword: str, page_count: int = 2) -> List[Dict]:
        """完整的商品采集流程"""
        products = []
        
        try:
            # 构建搜索URL
            encoded_keyword = urllib.parse.quote(keyword)
            search_url = f"https://www.tiktok.com/shop/s/{encoded_keyword}"
            
            print(f"🌐 访问TikTok搜索页面: {search_url}")
            
            # 访问搜索页面
            current_url, current_title = self.navigate_to_url(search_url)
            if not current_url:
                return products
            
            # 处理验证码
            print("🧩 检测和处理滑块验证...")
            if self.handle_captcha():
                print("❌ 验证码无法跳过，停止采集")
                return products
            
            print("✅ 滑块验证处理完成，开始解析页面数据")
            
            # 等待页面跳转
            time.sleep(5)
            
            # 获取页面组件数据
            print("📊 正在解析页面数据...")
            components_map = self.get_components_map()
            
            if not components_map:
                print("⚠️ 未能获取页面组件数据")
                return products
            
            # 提取第一页商品列表
            for component in components_map:
                if component.get("component_name") == "feed_list_search_word":
                    component_products = component.get("component_data", {}).get("products", [])
                    print(f"📦 找到 {len(component_products)} 个商品")
                    
                    for i, product in enumerate(component_products):
                        if not self.is_running:
                            break
                        
                        product_id = product.get("product_id")
                        if product_id:
                            print(f"📦 正在处理商品 {i+1}/{len(component_products)}: {product_id}")
                            product_data = self.parse_product_data(product, keyword)
                            if product_data:
                                products.append(product_data)
                                self.save_product_to_db(product_data)
                    break
            
            print(f"📦 第1页获取 {len(products)} 个商品")
            
            # 处理更多页面（简化版本）
            if self.is_running and page_count > 1:
                print(f"📄 开始获取更多页面数据，额外页数: {page_count - 1}")
                
                for page_num in range(page_count - 1):
                    try:
                        # 查找"View more"按钮
                        view_more_btn = self.page.ele("text=View more", timeout=5)
                        if view_more_btn:
                            view_more_btn.click()
                            time.sleep(3)
                            print(f"📄 已点击第 {page_num + 2} 页")
                        else:
                            print("⚠️ 未找到'View more'按钮，停止翻页")
                            break
                    except:
                        break
            
            print(f"🎉 总共采集到 {len(products)} 个商品")
            return products
            
        except Exception as e:
            print(f"❌ 采集失败: {e}")
            return products
    
    def run(self, keyword: str = "phone case", page_count: int = 2):
        """运行爬虫"""
        print("🎉 Crawlab TikTok Shop完整爬虫启动")
        print("=" * 60)
        print(f"搜索关键词: {keyword}")
        print(f"采集页数: {page_count}")
        print("=" * 60)
        
        try:
            # 初始化各个组件
            if not self.init_browser():
                return False
            
            if not self.init_ocr():
                return False
            
            if not self.init_database():
                return False
            
            # 获取初始商品数量
            initial_count = self.collection.count_documents({})
            
            # 开始采集
            start_time = time.time()
            products = self.scrape_keyword_products(keyword, page_count)
            end_time = time.time()
            
            # 获取最终商品数量
            final_count = self.collection.count_documents({})
            new_products = final_count - initial_count
            
            # 显示结果
            duration = end_time - start_time
            print(f"\n📊 采集结果汇总:")
            print(f"  ✅ 采集关键词: {keyword}")
            print(f"  ✅ 采集页数: {page_count}")
            print(f"  ✅ 采集商品数: {len(products)}")
            print(f"  ✅ 新增商品数: {new_products}")
            print(f"  ✅ 数据库总商品: {final_count}")
            print(f"  ✅ 采集耗时: {duration:.2f} 秒")
            
            print(f"\n🎊 Crawlab爬虫任务完成！")
            return True
            
        except Exception as e:
            print(f"❌ 爬虫运行失败: {e}")
            return False
        
        finally:
            self.close()
    
    def close(self):
        """关闭资源"""
        try:
            if self.page:
                self.page.quit()
            if self.mongo_client:
                self.mongo_client.close()
            print("✅ 资源清理完成")
        except:
            pass

def main():
    """主函数"""
    # 从环境变量或命令行参数获取配置
    keyword = os.getenv('CRAWLAB_KEYWORDS', 'phone case')
    page_count = int(os.getenv('CRAWLAB_MAX_PAGES', '2'))
    
    # 创建并运行爬虫
    spider = CrawlabTikTokSpider()
    success = spider.run(keyword, page_count)
    
    if success:
        print("🎉 爬虫任务执行成功")
        sys.exit(0)
    else:
        print("❌ 爬虫任务执行失败")
        sys.exit(1)

if __name__ == "__main__":
    if not DEPENDENCIES_OK:
        print("❌ 依赖检查失败，请确保安装了所有必需的包")
        sys.exit(1)
    
    main()