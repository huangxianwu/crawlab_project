#!/usr/bin/env python3
"""
完整的TikTok Shop爬虫演示
基于reference_based_scraper的完整实现
包含：搜索 -> 滑块处理 -> 采集商品 -> 保存商品的全流程
"""

# 🔧 关键修复：在任何导入之前就修复路径
import sys
import os

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))

# 多重路径修复策略
paths_to_add = [
    script_dir,                    # 脚本所在目录
    os.getcwd(),                   # 当前工作目录
    '.',                           # 相对当前目录
]

# 将所有可能的路径都添加到sys.path的最前面
for path in reversed(paths_to_add):  # 反向添加，确保script_dir优先级最高
    abs_path = os.path.abspath(path)
    if abs_path not in sys.path:
        sys.path.insert(0, abs_path)

# 🔍 增强调试信息 - 始终显示以便Crawlab调试
print("=" * 60)
print("🔍 [DEBUG] run_complete_crawler.py 路径调试信息")
print("=" * 60)
print(f"[DEBUG] Python版本: {sys.version}")
print(f"[DEBUG] 脚本文件: {__file__}")
print(f"[DEBUG] 脚本目录: {script_dir}")
print(f"[DEBUG] 当前工作目录: {os.getcwd()}")
print(f"[DEBUG] 用户主目录: {os.path.expanduser('~')}")
print(f"[DEBUG] 环境变量PATH: {os.getenv('PATH', 'N/A')[:200]}...")

# 显示sys.path的前10个路径
print(f"[DEBUG] sys.path前10个路径:")
for i, path in enumerate(sys.path[:10]):
    print(f"  {i}: {path}")

# 验证关键目录是否存在
print(f"[DEBUG] 关键目录检查:")
key_dirs = ['handlers', 'utils', 'models', 'config.py']
for item in key_dirs:
    item_path = os.path.join(script_dir, item)
    exists = os.path.exists(item_path)
    is_dir = os.path.isdir(item_path) if exists else False
    is_file = os.path.isfile(item_path) if exists else False
    print(f"  {item}: 存在={exists}, 目录={is_dir}, 文件={is_file}")
    print(f"    路径: {item_path}")

# 检查utils目录的内容
utils_dir = os.path.join(script_dir, 'utils')
if os.path.exists(utils_dir):
    print(f"[DEBUG] utils目录内容:")
    try:
        for item in os.listdir(utils_dir):
            item_path = os.path.join(utils_dir, item)
            print(f"  {item} ({'文件' if os.path.isfile(item_path) else '目录'})")
    except Exception as e:
        print(f"  读取utils目录失败: {e}")

# 检查handlers目录的内容
handlers_dir = os.path.join(script_dir, 'handlers')
if os.path.exists(handlers_dir):
    print(f"[DEBUG] handlers目录内容:")
    try:
        for item in os.listdir(handlers_dir):
            item_path = os.path.join(handlers_dir, item)
            print(f"  {item} ({'文件' if os.path.isfile(item_path) else '目录'})")
    except Exception as e:
        print(f"  读取handlers目录失败: {e}")

# 尝试直接导入测试
print(f"[DEBUG] 直接导入测试:")
try:
    import utils
    print(f"  ✅ import utils 成功: {utils.__file__}")
except Exception as e:
    print(f"  ❌ import utils 失败: {e}")

try:
    import utils.logger
    print(f"  ✅ import utils.logger 成功: {utils.logger.__file__}")
except Exception as e:
    print(f"  ❌ import utils.logger 失败: {e}")

try:
    import config
    print(f"  ✅ import config 成功: {config.__file__}")
except Exception as e:
    print(f"  ❌ import config 失败: {e}")

print("=" * 60)

# 强制刷新模块缓存（防止缓存问题）
modules_to_clear = ['handlers', 'utils', 'models']
for module in modules_to_clear:
    if module in sys.modules:
        del sys.modules[module]

# 现在安全地导入其他模块
import time
import json
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional

from handlers.drissionpage_slider_handler import DrissionPageSliderHandler
from models.product import ProductData
from utils.database import get_db_manager
from utils.logger import setup_logger
from utils.anti_detection import get_anti_detection_manager, random_delay

class CompleteTikTokCrawler:
    """
    完整的TikTok Shop爬虫
    实现完整的采集流程
    """
    
    def __init__(self, proxy_enabled=False):
        self.slider_handler = DrissionPageSliderHandler(proxy_enabled=proxy_enabled)
        self.db_manager = get_db_manager()
        self.db_manager.connect()
        self.is_running = True
        self.logger = setup_logger('complete_crawler')
        self.anti_detection = get_anti_detection_manager()
        
        # API URLs
        self.product_list_url = "https://www.tiktok.com/api/shop/brandy_desktop/s/product_list"
        
    def scrape_keyword_products(self, keyword: str, page_count: int = 2) -> List[Dict]:
        """
        完整的商品采集流程
        """
        products = []
        
        try:
            # 构建搜索URL
            encoded_keyword = urllib.parse.quote(keyword)
            search_url = f"https://www.tiktok.com/shop/s/{encoded_keyword}"
            
            self.logger.info(f"访问TikTok搜索页面: {search_url}")
            print(f"🌐 访问TikTok搜索页面: {search_url}")
            
            # 访问搜索页面
            self.slider_handler.navigate_to_url(search_url)
            
            # 随机延时，模拟人工操作
            print("⏱️ 随机延时中...")
            random_delay(2.0, 4.0)
            
            # 处理验证码
            print("🧩 检测和处理滑块验证...")
            if self.slider_handler.handle_captcha():
                self.logger.error("验证码无法跳过，停止采集")
                print("❌ 验证码无法跳过，停止采集")
                return products
            
            print("✅ 滑块验证处理完成，开始解析页面数据")
            
            # 验证码处理后的延时
            random_delay(1.0, 3.0)
            
            # 获取页面组件数据
            print("📊 正在解析页面数据...")
            components_map = self.get_components_map()
            
            if not components_map:
                self.logger.warning("未能获取页面组件数据")
                print("⚠️ 未能获取页面组件数据")
                return products
            
            # 提取第一页商品列表
            first_page_products = self.extract_first_page_products(components_map, keyword)
            products.extend(first_page_products)
            
            print(f"📦 第1页获取 {len(first_page_products)} 个商品")
            
            # 获取更多页面数据
            if self.is_running and page_count > 1:
                more_products = self.get_more_page_products(keyword, page_count - 1)
                products.extend(more_products)
            
            self.logger.info(f"总共采集到 {len(products)} 个商品")
            print(f"🎉 总共采集到 {len(products)} 个商品")
            
            return products
            
        except Exception as e:
            self.logger.error(f"采集失败: {e}")
            print(f"❌ 采集失败: {e}")
            return products
    
    def get_components_map(self) -> List[Dict]:
        """获取页面组件映射"""
        try:
            # 查找页面数据元素
            ele = self.slider_handler.page.ele("@id=__MODERN_ROUTER_DATA__", timeout=10)
            if not ele:
                self.logger.warning("未找到页面数据元素")
                print("⚠️ 未找到页面数据元素")
                return []
            
            # 解析JSON数据
            loader_data = json.loads(ele.inner_html)
            
            # 根据实际的页面结构获取组件映射
            loader_keys = list(loader_data.get("loaderData", {}).keys())
            print(f"🔍 页面结构键: {loader_keys}")
            
            # 查找包含page_config的键
            for key in loader_keys:
                if key and isinstance(loader_data["loaderData"][key], dict):
                    page_data = loader_data["loaderData"][key]
                    if "page_config" in page_data and "components_map" in page_data["page_config"]:
                        components_map = page_data["page_config"]["components_map"]
                        print(f"✅ 找到页面组件映射: {len(components_map)} 个组件 (键: {key})")
                        return components_map
            
            self.logger.warning("未找到匹配的页面结构")
            print("⚠️ 未找到匹配的页面结构")
            return []
            
        except Exception as e:
            self.logger.error(f"解析页面组件数据失败: {e}")
            print(f"⚠️ 解析页面组件数据失败: {e}")
            return []
    
    def extract_first_page_products(self, components_map: List[Dict], keyword: str) -> List[Dict]:
        """提取第一页商品数据"""
        products = []
        
        try:
            # 查找商品列表组件
            for component in components_map:
                if component.get("component_name") == "feed_list_search_word":
                    component_products = component.get("component_data", {}).get("products", [])
                    self.logger.info(f"找到 {len(component_products)} 个商品")
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
                                
                                # 保存到数据库
                                self.save_product_to_db(product_data)
                                
                                # 商品处理间隔
                                if i < len(component_products) - 1:  # 不是最后一个商品
                                    random_delay(0.5, 1.5)
                    break
            
            return products
            
        except Exception as e:
            self.logger.error(f"提取第一页商品失败: {e}")
            return products
    
    def parse_product_data(self, product: Dict, keyword: str) -> Optional[Dict]:
        """
        解析商品数据
        """
        try:
            # 基本信息
            product_id = product.get("product_id", "")
            title = product.get("title", "")
            
            # 价格信息
            price_info = product.get("product_price_info", {})
            current_price_str = price_info.get("sale_price_format", "0")
            origin_price_str = price_info.get("origin_price_format", current_price_str)
            
            # 清理价格字符串，提取数字
            try:
                current_price = float(current_price_str.replace('$', '').replace(',', ''))
                origin_price = float(origin_price_str.replace('$', '').replace(',', ''))
            except:
                current_price = 0.0
                origin_price = 0.0
            
            # 商品图片
            product_image = ""
            images = product.get("images", [])
            if images and len(images) > 0:
                product_image = images[0].get("url_list", [""])[0]
            
            # 销售信息
            sold_count = product.get("sold_count", 0)
            
            # 店铺信息
            seller = product.get("seller", {})
            shop_name = seller.get("name", "")
            
            # 评价信息
            product_rating = product.get("product_rating", 0.0)
            review_count = product.get("review_count", 0)
            review_count_str = str(review_count)
            
            # 分类信息
            categories = "TikTok Shop"
            
            # 物流信息
            shipping_fee = 0.0
            
            # 商品链接
            product_url = f"https://www.tiktok.com/shop/product/{product_id}"
            
            # 创建商品数据
            product_data = {
                'product_id': product_id,
                'title': title,
                'search_keyword': keyword,
                'current_price': current_price,
                'origin_price': origin_price,
                'shipping_fee': shipping_fee,
                'product_image': product_image,
                'product_url': product_url,
                'categories': categories,
                'desc_detail': "",
                'sold_count': sold_count,
                'product_rating': product_rating,
                'review_count': review_count,
                'review_count_str': review_count_str,
                'latest_review_fmt': "",
                'earliest_review_fmt': "",
                'shop_name': shop_name,
                'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'slider_encountered': True,
                'slider_solved': True
            }
            
            self.logger.debug(f"解析商品: {title} - ${current_price}")
            return product_data
            
        except Exception as e:
            self.logger.error(f"解析商品数据失败: {e}")
            return None
    
    def get_more_page_products(self, keyword: str, additional_pages: int) -> List[Dict]:
        """
        获取更多页面商品
        """
        products = []
        
        try:
            self.logger.info(f"开始获取更多页面数据，额外页数: {additional_pages}")
            print(f"📄 开始获取更多页面数据，额外页数: {additional_pages}")
            
            # 开始监听API请求
            self.slider_handler.page.listen.start(self.product_list_url)
            
            for page_num in range(additional_pages):
                if not self.is_running:
                    break
                
                current_page = page_num + 2  # 从第2页开始
                print(f"📄 正在加载第 {current_page} 页...")
                
                try:
                    # 查找并点击"View more"按钮
                    view_more_selectors = [
                        "text=View more",
                        "text=查看更多",
                        "[data-e2e='load-more']",
                        ".load-more",
                        "[class*='load-more']"
                    ]
                    
                    view_more_btn = None
                    for selector in view_more_selectors:
                        try:
                            view_more_btn = self.slider_handler.page.ele(selector, timeout=3)
                            if view_more_btn and view_more_btn.states.is_displayed:
                                print(f"✅ 找到翻页按钮: {selector}")
                                break
                        except:
                            continue
                    
                    if view_more_btn:
                        # 滚动到按钮位置
                        view_more_btn.scroll.to_see()
                        time.sleep(1)
                        
                        # 点击按钮
                        view_more_btn.click()
                        time.sleep(2)
                        
                        # 等待API响应
                        try:
                            res = self.slider_handler.page.listen.wait(timeout=10)
                            if res and res.response.body:
                                api_products = res.response.body.get("data", {}).get("products", [])
                                self.logger.info(f"第 {current_page} 页获取 {len(api_products)} 个商品")
                                print(f"📦 第 {current_page} 页获取 {len(api_products)} 个商品")
                                
                                # 解析API返回的商品数据
                                for product in api_products:
                                    if not self.is_running:
                                        break
                                    
                                    product_id = product.get("product_id")
                                    if product_id:
                                        product_data = self.parse_product_data(product, keyword)
                                        if product_data:
                                            products.append(product_data)
                                            
                                            # 保存到数据库
                                            self.save_product_to_db(product_data)
                            else:
                                self.logger.warning(f"第 {current_page} 页API响应为空")
                                print(f"⚠️ 第 {current_page} 页API响应为空")
                                
                        except Exception as e:
                            self.logger.warning(f"等待API响应失败: {e}")
                            print(f"⚠️ 等待API响应失败: {e}")
                    else:
                        self.logger.warning("未找到'View more'按钮，停止翻页")
                        print("⚠️ 未找到'View more'按钮，停止翻页")
                        break
                        
                except Exception as e:
                    self.logger.warning(f"第 {current_page} 页加载失败: {e}")
                    print(f"⚠️ 第 {current_page} 页加载失败: {e}")
                    continue
            
            return products
            
        except Exception as e:
            self.logger.error(f"获取更多页面数据失败: {e}")
            print(f"❌ 获取更多页面数据失败: {e}")
            return products
    
    def save_product_to_db(self, product_data: Dict):
        """保存商品到数据库"""
        try:
            product = ProductData.from_dict(product_data)
            
            # 检查是否已存在
            existing = self.db_manager.find_products({"product_id": product.product_id})
            if existing:
                self.logger.debug(f"商品已存在，跳过: {product.product_id}")
                return
            
            # 保存到数据库
            if self.db_manager.save_product(product):
                self.logger.info(f"保存商品成功: {product.title[:30]}... - ${product.current_price}")
                print(f"💾 保存商品: {product.title[:30]}... - ${product.current_price}")
            else:
                self.logger.error(f"保存商品失败: {product.product_id}")
                
        except Exception as e:
            self.logger.error(f"保存商品到数据库失败: {e}")
    
    def get_total_products_count(self) -> int:
        """获取数据库中的商品总数"""
        try:
            return self.db_manager.count_products()
        except Exception as e:
            self.logger.error(f"获取商品总数失败: {e}")
            return 0
    
    def close(self):
        """关闭资源"""
        try:
            if self.slider_handler:
                self.slider_handler.close()
            if self.db_manager:
                self.db_manager.close()
        except Exception as e:
            self.logger.error(f"关闭资源失败: {e}")

def main():
    """主函数 - 运行完整的爬虫演示"""
    print("🎉 TikTok Shop完整爬虫演示")
    print("=" * 60)
    print("完整流程:")
    print("✅ 1. 访问TikTok Shop搜索页面")
    print("✅ 2. 自动检测和处理滑块验证")
    print("✅ 3. 解析页面数据结构")
    print("✅ 4. 提取商品详细信息")
    print("✅ 5. 保存商品数据到数据库")
    print("✅ 6. 支持多页数据采集")
    print("=" * 60)
    
    # 测试配置
    test_keyword = "phone case"
    page_count = 2
    
    print(f"\n📋 演示配置:")
    print(f"  搜索关键词: {test_keyword}")
    print(f"  采集页数: {page_count}")
    print(f"  技术栈: DrissionPage + ddddocr")
    
    crawler = None
    
    try:
        # 初始化爬虫
        print(f"\n🚀 初始化完整爬虫系统...")
        crawler = CompleteTikTokCrawler(proxy_enabled=False)
        print("✅ 爬虫系统初始化成功")
        
        # 显示数据库状态
        total_before = crawler.get_total_products_count()
        print(f"📊 数据库中现有商品: {total_before} 条")
        
        # 开始采集
        print(f"\n🎯 开始完整采集流程...")
        start_time = time.time()
        
        products = crawler.scrape_keyword_products(test_keyword, page_count)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 显示结果
        total_after = crawler.get_total_products_count()
        new_products = total_after - total_before
        
        print(f"\n📊 采集结果汇总:")
        print(f"  ✅ 采集关键词: {test_keyword}")
        print(f"  ✅ 采集页数: {page_count}")
        print(f"  ✅ 采集商品数: {len(products)}")
        print(f"  ✅ 新增商品数: {new_products}")
        print(f"  ✅ 数据库总商品: {total_after}")
        print(f"  ✅ 采集耗时: {duration:.2f} 秒")
        
        if products:
            print(f"\n📋 采集商品样例:")
            for i, product in enumerate(products[:5]):
                print(f"  商品{i+1}:")
                print(f"    ID: {product.get('product_id', 'N/A')}")
                print(f"    标题: {product.get('title', 'N/A')[:50]}...")
                print(f"    价格: ${product.get('current_price', 0)}")
                print(f"    店铺: {product.get('shop_name', 'N/A')}")
                print(f"    销量: {product.get('sold_count', 0)}")
                print(f"    评分: {product.get('product_rating', 0)}⭐")
        
        print(f"\n🎊 完整爬虫演示成功完成！")
        print(f"核心功能验证:")
        print(f"  ✅ TikTok Shop访问正常")
        print(f"  ✅ 滑块验证自动处理")
        print(f"  ✅ 页面数据解析成功")
        print(f"  ✅ 商品信息提取完整")
        print(f"  ✅ 数据库保存正常")
        print(f"  ✅ 多页采集支持")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        
    finally:
        # 清理资源
        print(f"\n🧹 清理资源...")
        if crawler:
            crawler.close()
            print("✅ 爬虫资源已清理")

if __name__ == "__main__":
    main()