#!/usr/bin/env python3
"""
基于DrissionPage的TikTok商品采集器
直接移植参考项目的完整采集逻辑
"""
import time
import json
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional
from drissionpage_slider_handler import DrissionPageSliderHandler
from models.product import ProductData
from utils.database import DatabaseManager
from utils.logger import get_logger

logger = get_logger(__name__)

class TikTokProductScraper:
    """
    TikTok商品采集器
    基于参考项目的完整实现
    """
    
    def __init__(self, proxy_enabled=False):
        self.slider_handler = DrissionPageSliderHandler(proxy_enabled=proxy_enabled)
        self.db_manager = DatabaseManager()
        self.is_running = True
        
        # API URLs (基于参考项目)
        self.product_list_url = "https://www.tiktok.com/api/shop/brandy_desktop/s/product_list"
        
    def scrape_keyword_products(self, keyword: str, page_count: int = 2) -> List[Dict]:
        """
        采集关键词商品 - 基于参考项目的 scrape_keyword_products 方法
        
        Args:
            keyword: 搜索关键词
            page_count: 采集页数
            
        Returns:
            List[Dict]: 商品数据列表
        """
        products = []
        
        try:
            # 构建搜索URL
            encoded_keyword = urllib.parse.quote(keyword)
            search_url = f"https://www.tiktok.com/shop/s/{encoded_keyword}"
            
            logger.info(f"访问TikTok搜索页面: {search_url}")
            print(f"🌐 访问TikTok搜索页面: {search_url}")
            
            # 访问搜索页面
            self.slider_handler.navigate_to_url(search_url)
            
            # 处理验证码
            print("🔍 检查是否需要处理滑块验证...")
            if self.slider_handler.handle_captcha():
                logger.error("验证码无法跳过，停止采集")
                print("❌ 验证码无法跳过，停止采集")
                return products
            
            print("✅ 滑块验证通过，开始采集商品数据")
            
            # 获取页面组件数据
            print("📊 正在解析页面数据...")
            components_map = self.get_components_map()
            
            if not components_map:
                logger.warning("未能获取页面组件数据")
                print("⚠️ 未能获取页面组件数据")
                return products
            
            # 提取第一页商品列表
            first_page_products = self.extract_first_page_products(components_map, keyword)
            products.extend(first_page_products)
            
            print(f"📦 第1页获取 {len(first_page_products)} 个商品")
            
            # 获取更多页面数据
            if page_count > 1 and self.is_running:
                more_products = self.get_more_page_products(keyword, page_count - 1)
                products.extend(more_products)
            
            logger.info(f"总共采集到 {len(products)} 个商品")
            print(f"🎉 总共采集到 {len(products)} 个商品")
            
            return products
            
        except Exception as e:
            logger.error(f"采集失败: {e}")
            print(f"❌ 采集失败: {e}")
            return products
    
    def get_components_map(self) -> List[Dict]:
        """获取页面组件映射 - 基于参考项目，增加备用方案"""
        try:
            # 方法1: 查找页面数据元素
            ele = self.slider_handler.page.ele("@id=__MODERN_ROUTER_DATA__", timeout=10)
            if ele:
                try:
                    # 解析JSON数据
                    loader_data = json.loads(ele.inner_html)
                    
                    # 提取组件映射
                    components_map = []
                    if "loaderData" in loader_data:
                        for key, value in loader_data["loaderData"].items():
                            if isinstance(value, dict) and "components" in value:
                                components_map.extend(value["components"])
                    
                    if components_map:
                        logger.info(f"找到 {len(components_map)} 个页面组件")
                        return components_map
                except Exception as e:
                    logger.warning(f"解析页面数据失败: {e}")
            
            # 方法2: 直接从页面HTML中提取商品信息
            print("🔍 尝试直接从页面HTML中提取商品信息...")
            return self.extract_products_from_html()
            
        except Exception as e:
            logger.error(f"获取页面组件数据失败: {e}")
            return []
    
    def extract_products_from_html(self) -> List[Dict]:
        """直接从页面HTML中提取商品信息"""
        try:
            # 等待页面加载完成
            time.sleep(5)
            
            # 查找商品卡片元素
            product_selectors = [
                '[data-e2e="search-card-item"]',
                '.product-card',
                '.item-card',
                '[class*="product"]',
                '[class*="item"]',
                'a[href*="/product/"]'
            ]
            
            products = []
            for selector in product_selectors:
                try:
                    elements = self.slider_handler.page.eles(selector, timeout=3)
                    if elements:
                        print(f"✅ 找到 {len(elements)} 个商品元素 (选择器: {selector})")
                        
                        for i, element in enumerate(elements[:30]):  # 最多处理30个商品
                            try:
                                product_data = self.extract_product_from_element(element, i+1)
                                if product_data:
                                    products.append(product_data)
                            except Exception as e:
                                logger.debug(f"提取第{i+1}个商品失败: {e}")
                                continue
                        
                        if products:
                            break  # 找到商品就退出循环
                except:
                    continue
            
            # 如果还是没找到，尝试查找所有链接
            if not products:
                print("🔍 尝试从所有链接中查找商品...")
                products = self.extract_products_from_links()
            
            return [{"component_name": "feed_list_search_word", 
                    "component_data": {"products": products}}] if products else []
            
        except Exception as e:
            logger.error(f"从HTML提取商品失败: {e}")
            return []
    
    def extract_product_from_element(self, element, index: int) -> Optional[Dict]:
        """从元素中提取商品信息"""
        try:
            # 提取标题
            title = ""
            title_selectors = ['[data-e2e="search-card-title"]', '.title', 'h3', 'h4', '[class*="title"]']
            for selector in title_selectors:
                try:
                    title_elem = element.ele(selector, timeout=1)
                    if title_elem:
                        title = title_elem.text.strip()
                        break
                except:
                    continue
            
            # 如果没有找到标题，尝试从文本内容中提取
            if not title:
                title = element.text.strip()[:100] if element.text else f"商品{index}"
            
            # 提取价格
            price_str = "0"
            price_selectors = ['[data-e2e="search-card-price"]', '.price', '[class*="price"]', '[class*="cost"]']
            for selector in price_selectors:
                try:
                    price_elem = element.ele(selector, timeout=1)
                    if price_elem:
                        price_str = price_elem.text.strip()
                        break
                except:
                    continue
            
            # 提取图片
            image_url = ""
            try:
                img_elem = element.ele('img', timeout=1)
                if img_elem:
                    image_url = img_elem.attr('src') or ''
            except:
                pass
            
            # 提取链接
            link_url = ""
            try:
                if element.tag == 'a':
                    link_url = element.attr('href') or ''
                else:
                    link_elem = element.ele('a', timeout=1)
                    if link_elem:
                        link_url = link_elem.attr('href') or ''
            except:
                pass
            
            # 生成商品ID
            product_id = f"product_{index}_{int(time.time())}"
            
            # 如果有标题或价格，认为是有效商品
            if title and len(title) > 3:
                return {
                    "product_id": product_id,
                    "title": title,
                    "product_price_info": {
                        "sale_price_format": price_str,
                        "origin_price_format": price_str
                    },
                    "images": [{"url_list": [image_url]}] if image_url else [],
                    "sold_count": 0,
                    "seller": {"name": ""},
                    "product_rating": 0.0,
                    "review_count": 0
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"提取商品{index}信息失败: {e}")
            return None
    
    def extract_products_from_links(self) -> List[Dict]:
        """从页面链接中提取商品信息"""
        try:
            # 查找所有链接
            links = self.slider_handler.page.eles('a', timeout=5)
            products = []
            
            for i, link in enumerate(links[:50]):  # 检查前50个链接
                try:
                    href = link.attr('href') or ''
                    text = link.text.strip()
                    
                    # 检查是否是商品链接
                    if ('/product/' in href or 'item' in href.lower()) and text and len(text) > 5:
                        product_id = f"link_product_{i}_{int(time.time())}"
                        
                        products.append({
                            "product_id": product_id,
                            "title": text[:100],
                            "product_price_info": {
                                "sale_price_format": "0",
                                "origin_price_format": "0"
                            },
                            "images": [],
                            "sold_count": 0,
                            "seller": {"name": ""},
                            "product_rating": 0.0,
                            "review_count": 0
                        })
                        
                        if len(products) >= 20:  # 最多找20个
                            break
                except:
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"从链接提取商品失败: {e}")
            return []
    
    def extract_first_page_products(self, components_map: List[Dict], keyword: str) -> List[Dict]:
        """提取第一页商品数据"""
        products = []
        
        try:
            # 查找商品列表组件
            for component in components_map:
                if component.get("component_name") == "feed_list_search_word":
                    component_products = component.get("component_data", {}).get("products", [])
                    logger.info(f"找到 {len(component_products)} 个商品")
                    
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
                    break
            
            return products
            
        except Exception as e:
            logger.error(f"提取第一页商品失败: {e}")
            return products
    
    def get_more_page_products(self, keyword: str, additional_pages: int) -> List[Dict]:
        """
        获取更多页面商品 - 基于参考项目的 get_more_page_products 方法
        
        Args:
            keyword: 搜索关键词
            additional_pages: 额外页数
            
        Returns:
            List[Dict]: 商品数据列表
        """
        products = []
        
        try:
            logger.info(f"开始获取更多页面数据，额外页数: {additional_pages}")
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
                                logger.info(f"第 {current_page} 页获取 {len(api_products)} 个商品")
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
                                logger.warning(f"第 {current_page} 页API响应为空")
                                print(f"⚠️ 第 {current_page} 页API响应为空")
                                
                        except Exception as e:
                            logger.warning(f"等待API响应失败: {e}")
                            print(f"⚠️ 等待API响应失败: {e}")
                    else:
                        logger.warning("未找到'View more'按钮，停止翻页")
                        print("⚠️ 未找到'View more'按钮，停止翻页")
                        break
                        
                except Exception as e:
                    logger.warning(f"第 {current_page} 页加载失败: {e}")
                    print(f"⚠️ 第 {current_page} 页加载失败: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"获取更多页面数据失败: {e}")
            print(f"❌ 获取更多页面数据失败: {e}")
            return products
    
    def parse_product_data(self, product: Dict, keyword: str) -> Optional[Dict]:
        """
        解析商品数据 - 基于参考项目的 parse_product_data 方法
        
        Args:
            product: 原始商品数据
            keyword: 搜索关键词
            
        Returns:
            Optional[Dict]: 解析后的商品数据
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
            
            # 创建商品数据
            product_data = {
                'product_id': product_id,
                'title': title,
                'search_keyword': keyword,
                'current_price': current_price,
                'origin_price': origin_price,
                'shipping_fee': shipping_fee,
                'product_image': product_image,
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
            
            logger.debug(f"解析商品: {title} - ${current_price}")
            return product_data
            
        except Exception as e:
            logger.error(f"解析商品数据失败: {e}")
            return None
    
    def save_product_to_db(self, product_data: Dict):
        """保存商品到数据库"""
        try:
            product = ProductData.from_dict(product_data)
            
            # 检查是否已存在
            existing = self.db_manager.find_products({"product_id": product.product_id})
            if existing:
                logger.debug(f"商品已存在，跳过: {product.product_id}")
                return
            
            # 保存到数据库
            if self.db_manager.save_product(product):
                logger.info(f"保存商品成功: {product.title[:30]}... - ${product.current_price}")
                print(f"💾 保存商品: {product.title[:30]}... - ${product.current_price}")
            else:
                logger.error(f"保存商品失败: {product.product_id}")
                
        except Exception as e:
            logger.error(f"保存商品到数据库失败: {e}")
    
    def get_total_products_count(self) -> int:
        """获取数据库中的商品总数"""
        try:
            return self.db_manager.count_products()
        except Exception as e:
            logger.error(f"获取商品总数失败: {e}")
            return 0
    
    def close(self):
        """关闭资源"""
        try:
            if self.slider_handler:
                self.slider_handler.close()
            if self.db_manager:
                self.db_manager.close()
        except Exception as e:
            logger.error(f"关闭资源失败: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()