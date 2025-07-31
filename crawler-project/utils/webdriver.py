"""
WebDriver管理器
基于TikTok项目经验，提供浏览器自动化功能
参考: https://github.com/huangxianwu/tiktok_web_crawler_pyqt
"""
import os
import time
import random
from typing import Optional, Dict, Any, List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class WebDriverManager:
    """WebDriver管理器 - 基于TikTok项目经验"""
    
    def __init__(self, headless: bool = None, proxy: str = None):
        """
        初始化WebDriver管理器
        
        Args:
            headless: 是否使用无头模式，None时从配置读取
            proxy: 代理服务器地址
        """
        self.driver: Optional[webdriver.Chrome] = None
        self.headless = headless if headless is not None else Config.HEADLESS_MODE
        self.proxy = proxy
        self.current_user_agent = None
        self.current_window_size = None
        
        logger.info(f"WebDriver管理器初始化 - 无头模式: {self.headless}")
    
    def create_driver(self) -> webdriver.Chrome:
        """
        创建Chrome WebDriver实例
        配置反检测参数和性能优化
        
        Returns:
            webdriver.Chrome: Chrome驱动实例
        """
        try:
            # 创建Chrome选项
            chrome_options = Options()
            
            # 基础配置
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # 反检测配置（基于TikTok项目经验）
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')  # 禁用图片加载提高速度
            chrome_options.add_argument('--disable-javascript')  # 根据需要可以启用
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            
            # 性能优化配置
            chrome_options.add_argument('--memory-pressure-off')
            chrome_options.add_argument('--max_old_space_size=4096')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            
            # 随机User-Agent
            self.current_user_agent = random.choice(Config.USER_AGENTS)
            chrome_options.add_argument(f'--user-agent={self.current_user_agent}')
            
            # 随机窗口大小
            self.current_window_size = random.choice(Config.WINDOW_SIZES)
            chrome_options.add_argument(f'--window-size={self.current_window_size[0]},{self.current_window_size[1]}')
            
            # 代理配置
            if self.proxy:
                chrome_options.add_argument(f'--proxy-server={self.proxy}')
                logger.info(f"使用代理: {self.proxy}")
            
            # 实验性功能
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 设置首选项
            prefs = {
                'profile.default_content_setting_values': {
                    'notifications': 2,  # 禁用通知
                    'images': 2,  # 禁用图片
                    'plugins': 2,  # 禁用插件
                    'popups': 2,  # 禁用弹窗
                    'geolocation': 2,  # 禁用地理位置
                    'media_stream': 2,  # 禁用媒体流
                },
                'profile.managed_default_content_settings': {
                    'images': 2
                }
            }
            chrome_options.add_experimental_option('prefs', prefs)
            
            # 创建Service
            service = Service(ChromeDriverManager().install())
            
            # 创建WebDriver实例
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 设置页面加载超时
            self.driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(Config.ELEMENT_WAIT_TIMEOUT)
            
            # 执行反检测脚本
            self.execute_anti_detection_script()
            
            logger.info(f"Chrome WebDriver创建成功")
            logger.info(f"User-Agent: {self.current_user_agent}")
            logger.info(f"窗口大小: {self.current_window_size}")
            
            return self.driver
            
        except Exception as e:
            logger.error(f"创建WebDriver失败: {e}")
            raise WebDriverException(f"WebDriver创建失败: {e}")
    
    def execute_anti_detection_script(self):
        """
        执行反检测脚本
        基于TikTok项目的反检测经验
        """
        try:
            if not self.driver:
                return
            
            # 隐藏webdriver属性
            anti_detection_script = """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // 伪造Chrome对象
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // 伪造插件信息
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // 伪造语言信息
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en'],
            });
            
            // 移除自动化标识
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """
            
            self.driver.execute_script(anti_detection_script)
            logger.debug("反检测脚本执行完成")
            
        except Exception as e:
            logger.warning(f"执行反检测脚本失败: {e}")
    
    def get_driver(self) -> webdriver.Chrome:
        """
        获取WebDriver实例
        如果不存在则创建新实例
        
        Returns:
            webdriver.Chrome: Chrome驱动实例
        """
        if not self.driver:
            self.create_driver()
        return self.driver
    
    def navigate_to_url(self, url: str, wait_for_element: str = None) -> bool:
        """
        导航到指定URL
        
        Args:
            url: 目标URL
            wait_for_element: 等待的元素选择器
            
        Returns:
            bool: 导航是否成功
        """
        try:
            if not self.driver:
                self.create_driver()
            
            logger.info(f"导航到URL: {url}")
            self.driver.get(url)
            
            # 随机等待
            time.sleep(random.uniform(2, 4))
            
            # 等待特定元素加载
            if wait_for_element:
                wait = WebDriverWait(self.driver, Config.ELEMENT_WAIT_TIMEOUT)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
                logger.debug(f"等待元素加载完成: {wait_for_element}")
            
            return True
            
        except TimeoutException:
            logger.error(f"页面加载超时: {url}")
            return False
        except Exception as e:
            logger.error(f"导航失败: {e}")
            return False
    
    def search_products(self, keyword: str) -> bool:
        """
        搜索商品
        基于TikTok Shop的搜索流程
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            bool: 搜索是否成功
        """
        try:
            # 构建搜索URL
            search_url = f"{Config.TARGET_URL}?q={keyword}"
            
            # 导航到搜索页面
            if not self.navigate_to_url(search_url):
                return False
            
            logger.info(f"搜索关键词: {keyword}")
            
            # 等待搜索结果加载
            wait = WebDriverWait(self.driver, Config.ELEMENT_WAIT_TIMEOUT)
            
            try:
                # 等待商品卡片出现
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, Config.PRODUCT_CARD_SELECTOR)))
                logger.info("搜索结果加载完成")
                return True
                
            except TimeoutException:
                logger.warning("搜索结果加载超时，可能需要处理验证码")
                return False
            
        except Exception as e:
            logger.error(f"搜索商品失败: {e}")
            return False
    
    def extract_products_from_page(self, keyword: str, page_num: int = 1) -> List[Dict[str, Any]]:
        """
        从当前页面提取商品信息
        
        Args:
            keyword: 搜索关键词
            page_num: 页面编号
            
        Returns:
            List[Dict]: 商品信息列表
        """
        products = []
        
        try:
            # 等待页面加载
            time.sleep(random.uniform(2, 4))
            
            # 查找商品卡片
            product_cards = self.driver.find_elements(By.CSS_SELECTOR, Config.PRODUCT_CARD_SELECTOR)
            
            if not product_cards:
                # 尝试其他选择器
                alternative_selectors = [
                    "[data-e2e*='product']",
                    ".product-item",
                    ".goods-item",
                    "[class*='product-card']"
                ]
                
                for selector in alternative_selectors:
                    product_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if product_cards:
                        logger.info(f"使用备用选择器找到商品: {selector}")
                        break
            
            logger.info(f"页面 {page_num} 找到 {len(product_cards)} 个商品卡片")
            
            # 提取每个商品的信息
            for i, card in enumerate(product_cards):
                try:
                    product_data = self.extract_product_data(card, keyword, i + 1)
                    if product_data:
                        products.append(product_data)
                        
                except Exception as e:
                    logger.warning(f"提取第 {i+1} 个商品信息失败: {e}")
                    continue
            
            logger.info(f"成功提取 {len(products)} 个商品信息")
            return products
            
        except Exception as e:
            logger.error(f"提取商品信息失败: {e}")
            return products
    
    def extract_product_data(self, card_element, keyword: str, index: int) -> Optional[Dict[str, Any]]:
        """
        从商品卡片元素提取商品数据
        
        Args:
            card_element: 商品卡片元素
            keyword: 搜索关键词
            index: 商品索引
            
        Returns:
            Dict: 商品数据，提取失败返回None
        """
        try:
            product_data = {
                'keyword': keyword,
                'scraped_at': time.time(),
                'slider_encountered': False,
                'slider_solved': False
            }
            
            # 提取商品标题
            try:
                title_element = card_element.find_element(By.CSS_SELECTOR, Config.PRODUCT_TITLE_SELECTOR)
                product_data['title'] = title_element.text.strip()
            except:
                # 尝试备用选择器
                title_selectors = ['h3', '.title', '[class*="title"]', 'a']
                for selector in title_selectors:
                    try:
                        title_element = card_element.find_element(By.CSS_SELECTOR, selector)
                        product_data['title'] = title_element.text.strip()
                        break
                    except:
                        continue
                
                if 'title' not in product_data:
                    product_data['title'] = f"商品 {index}"
            
            # 提取商品价格
            try:
                price_element = card_element.find_element(By.CSS_SELECTOR, Config.PRODUCT_PRICE_SELECTOR)
                price_text = price_element.text.strip()
                # 提取数字价格
                import re
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    product_data['price'] = float(price_match.group())
                else:
                    product_data['price'] = 0.0
            except:
                product_data['price'] = 0.0
            
            # 提取商品链接
            try:
                link_element = card_element.find_element(By.CSS_SELECTOR, Config.PRODUCT_LINK_SELECTOR)
                product_data['url'] = link_element.get_attribute('href')
            except:
                product_data['url'] = ''
            
            # 提取商品图片
            try:
                img_element = card_element.find_element(By.CSS_SELECTOR, Config.PRODUCT_IMAGE_SELECTOR)
                product_data['image_url'] = img_element.get_attribute('src')
            except:
                product_data['image_url'] = ''
            
            # 提取店铺名称
            try:
                shop_element = card_element.find_element(By.CSS_SELECTOR, Config.PRODUCT_SHOP_SELECTOR)
                product_data['shop_name'] = shop_element.text.strip()
            except:
                product_data['shop_name'] = ''
            
            # 提取评分
            try:
                rating_element = card_element.find_element(By.CSS_SELECTOR, Config.PRODUCT_RATING_SELECTOR)
                rating_text = rating_element.text.strip()
                import re
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    product_data['rating'] = float(rating_match.group())
                else:
                    product_data['rating'] = 0.0
            except:
                product_data['rating'] = 0.0
            
            # 提取销量
            try:
                sales_element = card_element.find_element(By.CSS_SELECTOR, Config.PRODUCT_SALES_SELECTOR)
                sales_text = sales_element.text.strip()
                import re
                sales_match = re.search(r'(\d+)', sales_text.replace(',', ''))
                if sales_match:
                    product_data['sales_count'] = int(sales_match.group())
                else:
                    product_data['sales_count'] = 0
            except:
                product_data['sales_count'] = 0
            
            # 生成商品ID
            import hashlib
            id_source = f"{product_data['title']}{product_data['price']}{keyword}{index}"
            product_data['product_id'] = hashlib.md5(id_source.encode()).hexdigest()[:12]
            
            logger.debug(f"提取商品数据: {product_data['title']}")
            return product_data
            
        except Exception as e:
            logger.error(f"提取商品数据失败: {e}")
            return None
    
    def scroll_page(self, scroll_count: int = 3):
        """
        滚动页面加载更多内容
        
        Args:
            scroll_count: 滚动次数
        """
        try:
            for i in range(scroll_count):
                # 滚动到页面底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))
                
                # 滚动回顶部
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(random.uniform(0.5, 1))
                
            logger.debug(f"页面滚动完成: {scroll_count} 次")
            
        except Exception as e:
            logger.warning(f"页面滚动失败: {e}")
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        截取当前页面截图
        
        Args:
            filename: 截图文件名，None时自动生成
            
        Returns:
            str: 截图文件路径
        """
        try:
            if not self.driver:
                return ""
            
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            # 确保截图目录存在
            os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)
            
            screenshot_path = os.path.join(Config.SCREENSHOT_DIR, filename)
            self.driver.save_screenshot(screenshot_path)
            
            logger.info(f"截图保存: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return ""
    
    def close_driver(self):
        """关闭WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("WebDriver已关闭")
        except Exception as e:
            logger.error(f"关闭WebDriver失败: {e}")
    
    def get_driver_status(self) -> Dict[str, Any]:
        """
        获取WebDriver状态信息
        
        Returns:
            Dict: 状态信息
        """
        status = {
            'driver_active': self.driver is not None,
            'current_url': '',
            'page_title': '',
            'user_agent': self.current_user_agent,
            'window_size': self.current_window_size,
            'proxy': self.proxy,
            'headless': self.headless
        }
        
        try:
            if self.driver:
                status['current_url'] = self.driver.current_url
                status['page_title'] = self.driver.title
        except Exception as e:
            logger.debug(f"获取驱动状态失败: {e}")
        
        return status
    
    def __del__(self):
        """析构函数，确保资源清理"""
        self.close_driver()