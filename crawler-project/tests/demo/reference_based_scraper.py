#!/usr/bin/env python3
"""
基于参考项目的TikTok商品采集器
直接移植参考项目的完整实现逻辑
"""
import time
import json
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.drissionpage_slider_handler import DrissionPageSliderHandler
from models.product import ProductData
from utils.database import DatabaseManager
from utils.logger import get_logger

logger = get_logger(__name__)

class ReferenceBasedScraper:
    """
    基于参考项目的TikTok商品采集器
    完全按照参考项目的方法实现
    """
    
    def __init__(self, proxy_enabled=False):
        self.slider_handler = DrissionPageSliderHandler(proxy_enabled=proxy_enabled)
        self.db_manager = DatabaseManager()
        self.db_manager.connect()
        self.is_running = True
        
        # API URLs - 直接来自参考项目
        self.product_list_url = "https://www.tiktok.com/api/shop/brandy_desktop/s/product_list"
        
    def scrape_keyword_products(self, keyword: str, page_count: int = 2) -> List[Dict]:
        """
        真实采集关键词商品 - 直接移植参考项目的 scrape_keyword_products 方法
        """
        products = []
        
        try:
            # 构建搜索URL - 参考项目的方法
            encoded_keyword = urllib.parse.quote(keyword)
            search_url = f"https://www.tiktok.com/shop/s/{encoded_keyword}"
            
            logger.info(f"访问TikTok搜索页面: {search_url}")
            print(f"🌐 访问TikTok搜索页面: {search_url}")
            
            # 访问搜索页面 - 参考项目的方法
            self.slider_handler.navigate_to_url(search_url)
            
            # 处理验证码 - 参考项目的方法
            if self.slider_handler.handle_captcha():
                logger.error("验证码无法跳过，停止采集")
                print("❌ 验证码无法跳过，停止采集")
                return products
            
            print("✅ 验证码处理完成，开始解析页面数据")
            
            # 获取页面组件数据 - 参考项目的 get_components_map 方法
            print("📊 正在解析页面数据...")
            components_map = self.get_components_map()
            
            if not components_map:
                logger.warning("未能获取页面组件数据")
                print("⚠️ 未能获取页面组件数据")
                return products
            
            # 提取商品列表 - 参考项目的逻辑
            for component in components_map:
                if component.get("component_name") == "feed_list_search_word":
                    component_products = component.get("component_data", {}).get("products", [])
                    logger.info(f"找到 {len(component_products)} 个商品")
                    print(f"📦 找到 {len(component_products)} 个商品")
                    
                    for i, product in enumerate(component_products):
                        if not self.is_running:
                            break
                        
                        product_id = product.get("product_id")
                        if product_id:
                            print(f"📦 正在处理商品 {i+1}/{len(component_products)}: {product_id}")
                            product_data = self.get_product_detail(product_id, keyword, product)
                            if product_data:
                                products.append(product_data)
                                
                                # 保存到数据库 - 参考项目的方法
                                self.save_product_to_db(product_data)
                    break
            
            # 获取更多页面数据 - 参考项目的 get_more_page_products 方法
            if self.is_running and page_count > 1:
                more_products = self.get_more_page_products(keyword, page_count - 1)
                products.extend(more_products)
            
            logger.info(f"总共采集到 {len(products)} 个商品")
            print(f"🎉 总共采集到 {len(products)} 个商品")
            
            return products
            
        except Exception as e:
            logger.error(f"真实采集失败: {e}")
            print(f"❌ 真实采集失败: {e}")
            return products
    
    def get_components_map(self) -> List[Dict]:
        """
        获取页面组件映射 - 直接移植参考项目的方法
        """
        try:
            # 查找页面数据元素 - 参考项目的方法
            ele = self.slider_handler.page.ele("@id=__MODERN_ROUTER_DATA__", timeout=10)
            if not ele:
                logger.warning("未找到页面数据元素")
                print("⚠️ 未找到页面数据元素")
                return []
            
            # 解析JSON数据 - 参考项目的方法
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
            
            logger.warning("未找到匹配的页面结构")
            print("⚠️ 未找到匹配的页面结构")
            return []
            
        except Exception as e:
            logger.error(f"解析页面组件数据失败: {e}")
            print(f"⚠️ 解析页面组件数据失败: {e}")
            return []
    
    def get_product_detail(self, product_id: str, keyword: str, basic_product: Dict) -> Optional[Dict]:
        """
        获取商品详细信息 - 直接移植参考项目的 get_product_detail 方法
        """
        try:
            # 构建商品详情URL - 参考项目的方法
            detail_url = f"https://www.tiktok.com/view/product/{product_id}?source=product_detail&enter_from=product_detail&enter_method=bread_crumbs"
            logger.debug(f"获取商品详情: {product_id}")
            
            # 创建新标签页 - 参考项目的方法
            tab = self.slider_handler.page.new_tab()
            tab.set.load_mode.eager()
            tab.get(detail_url)
            
            # 处理验证码 - 参考项目的方法
            if self.slider_handler.handle_captcha(tab):
                logger.warning(f"商品 {product_id} 验证码无法跳过")
                tab.close()
                return None
            
            # 获取商品详情组件数据 - 参考项目的方法
            components_map = self.get_components_map_from_tab(tab)
            
            product_data = None
            for component in components_map:
                if component.get("component_type") == "product_info":
                    product_data = self.parse_product_data(component.get("component_data", {}), keyword, basic_product)
                    product_data["product_url"] = detail_url
                    break
            
            tab.close()
            
            if not product_data:
                logger.warning(f"商品 {product_id} 数据为空")
            
            return product_data
            
        except Exception as e:
            logger.warning(f"获取商品 {product_id} 详情失败: {e}")
            return None
    
    def get_components_map_from_tab(self, tab) -> List[Dict]:
        """
        从标签页获取组件映射 - 直接移植参考项目的方法
        """
        try:
            ele = tab.ele("@id=__MODERN_ROUTER_DATA__", timeout=10)
            if not ele:
                return []
            
            loader_data = json.loads(ele.inner_html)
            
            if "view/product/(product_id)/page" in loader_data.get("loaderData", {}):
                return loader_data["loaderData"]["view/product/(product_id)/page"]["page_config"]["components_map"]
            
            return []
            
        except Exception:
            return []
    
    def parse_product_data(self, component_data: Dict, keyword: str, basic_product: Dict) -> Dict:
        """
        解析商品数据 - 直接移植参考项目的 parse_product_data 方法
        """
        try:
            product_info = component_data.get("product_info", {})
            
            # 基本信息 - 参考项目的字段
            product_id = product_info.get("product_id", "")
            title = product_info.get("product_base", {}).get("title", "")
            sold_count = product_info.get("product_base", {}).get("sold_count", 0)
            
            # 价格信息 - 参考项目的处理方式
            price_info = basic_product.get("product_price_info", {})
            current_price = price_info.get("sale_price_format", "0")
            origin_price = price_info.get("origin_price_format", current_price)
            
            # 清理价格字符串，提取数字 - 参考项目的方法
            try:
                current_price = float(current_price.replace('$', '').replace(',', ''))
                origin_price = float(origin_price.replace('$', '').replace(',', ''))
            except:
                current_price = 0.0
                origin_price = 0.0
            
            # 店铺信息 - 参考项目的字段
            seller = product_info.get("seller", {})
            shop_name = seller.get("name", "")
            
            # 物流信息 - 参考项目的字段
            shipping_fee = 0.0
            logistic = product_info.get("logistic", {})
            if logistic and "shipping_fee" in logistic:
                try:
                    shipping_fee = float(logistic["shipping_fee"].get("price_val", 0))
                except:
                    shipping_fee = 0.0
            
            # 评价信息 - 参考项目的字段
            product_rating = 0.0
            review_count_str = "0"
            latest_review_fmt = ""
            earliest_review_fmt = ""
            
            review_detail = product_info.get("product_detail_review", {})
            if review_detail:
                product_rating = review_detail.get("product_rating", 0.0)
                review_count_str = review_detail.get("review_count_str", "0")
                
                # 尝试获取评论时间信息
                try:
                    # 从评论详情中获取时间信息
                    reviews = review_detail.get("reviews", [])
                    if reviews:
                        # 获取最新评论时间
                        latest_review = reviews[0] if reviews else {}
                        latest_review_fmt = latest_review.get("create_time", "")
                        
                        # 获取最早评论时间
                        earliest_review = reviews[-1] if reviews else {}
                        earliest_review_fmt = earliest_review.get("create_time", "")
                except:
                    pass
                
                # 如果从评论详情中获取不到，尝试从其他字段获取
                if not latest_review_fmt:
                    latest_review_fmt = review_detail.get("latest_review_time", "")
                if not earliest_review_fmt:
                    earliest_review_fmt = review_detail.get("earliest_review_time", "")
            
            # 图片信息 - 参考项目的字段
            product_image = ""
            images = product_info.get("product_base", {}).get("images", [])
            if images:
                product_image = images[0].get("url_list", [""])[0]
            
            # 商品链接 - 新增字段
            product_url = ""
            try:
                # 构建商品链接
                product_url = f"https://www.tiktok.com/shop/product/{product_id}"
            except:
                pass
            
            # 分类信息 - 参考项目的字段
            categories = "TikTok Shop"
            
            # 商品描述 - 参考项目的字段
            desc_detail = ""
            try:
                desc_detail_json = json.loads(product_info.get("product_base", {}).get("desc_detail", "[]"))
                for item in desc_detail_json:
                    if item.get("type") == "text":
                        desc_detail += item.get("text", "")
                    elif item.get("type") == "ul":
                        desc_detail += " ".join(item.get("content", []))
            except:
                pass
            
            # 返回完整的商品数据 - 参考项目的数据结构
            return {
                'product_id': product_id,
                'title': title,
                'categories': categories,
                'origin_price': origin_price,
                'current_price': current_price,
                'product_image': product_image,
                'product_url': product_url,  # 新增：商品链接
                'shipping_fee': shipping_fee,
                'sold_count': sold_count,
                'product_rating': product_rating,
                'review_count': int(review_count_str.replace('k', '000').replace('K', '000').replace(',', '')) if review_count_str.replace('k', '').replace('K', '').replace(',', '').isdigit() else 0,
                'review_count_str': review_count_str,
                'latest_review_fmt': latest_review_fmt,
                'earliest_review_fmt': earliest_review_fmt,
                'shop_name': shop_name,
                'search_keyword': keyword,
                'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'desc_detail': desc_detail
            }
            
        except Exception as e:
            logger.warning(f"解析商品数据失败: {e}")
            return {}
    
    def get_more_page_products(self, keyword: str, additional_pages: int) -> List[Dict]:
        """
        获取更多页面商品 - 直接移植参考项目的 get_more_page_products 方法
        """
        products = []
        
        try:
            logger.info(f"开始获取更多页面数据，额外页数: {additional_pages}")
            print(f"📄 开始获取更多页面数据，额外页数: {additional_pages}")
            
            # 开始监听API请求 - 参考项目的方法
            self.slider_handler.page.listen.start(self.product_list_url)
            
            for page_num in range(additional_pages):
                if not self.is_running:
                    break
                
                current_page = page_num + 2  # 从第2页开始
                print(f"📄 正在加载第 {current_page} 页...")
                
                try:
                    # 点击"View more"按钮 - 参考项目的方法
                    view_more_btn = self.slider_handler.page.ele("text=View more", timeout=5)
                    if view_more_btn:
                        view_more_btn.click()
                        time.sleep(2)
                        
                        # 等待API响应 - 参考项目的方法
                        res = self.slider_handler.page.listen.wait(timeout=10)
                        if res and res.response.body:
                            api_products = res.response.body.get("data", {}).get("products", [])
                            logger.info(f"第 {current_page} 页获取 {len(api_products)} 个商品")
                            print(f"📦 第 {current_page} 页获取 {len(api_products)} 个商品")
                            
                            for product in api_products:
                                if not self.is_running:
                                    break
                                
                                product_id = product.get("product_id")
                                if product_id:
                                    product_data = self.get_product_detail(product_id, keyword, product)
                                    if product_data:
                                        products.append(product_data)
                                        
                                        # 保存到数据库 - 参考项目的方法
                                        self.save_product_to_db(product_data)
                        else:
                            logger.warning(f"第 {current_page} 页API响应为空")
                            print(f"⚠️ 第 {current_page} 页API响应为空")
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
    
    def save_product_to_db(self, product_data: Dict):
        """
        保存商品到数据库 - 参考项目的方法
        """
        try:
            product = ProductData.from_dict(product_data)
            
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