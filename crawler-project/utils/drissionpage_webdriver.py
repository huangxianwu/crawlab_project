#!/usr/bin/env python3
"""
基于DrissionPage的WebDriver工具
替代Selenium，提供更好的滑块处理能力
"""
import time
from typing import Optional
from DrissionPage import ChromiumPage, ChromiumOptions
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class DrissionPageWebDriver:
    """
    基于DrissionPage的WebDriver封装
    提供与Selenium兼容的接口，同时支持原生滑块处理
    """
    
    def __init__(self, proxy_enabled=False):
        self.page = None
        self.proxy_enabled = proxy_enabled
        self.init_browser()
    
    def init_browser(self):
        """初始化浏览器"""
        try:
            logger.info("正在启动Chrome浏览器...")
            co = ChromiumOptions()
            
            # 添加稳定性参数
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-dev-shm-usage')
            co.set_argument('--disable-gpu')
            co.set_argument('--disable-web-security')
            co.set_argument('--allow-running-insecure-content')
            
            # 设置代理
            if self.proxy_enabled and hasattr(Config, 'PROXY_HOST'):
                proxy_address = f"http://{Config.PROXY_HOST}:{Config.PROXY_PORT}"
                co.set_proxy(proxy_address)
                logger.info(f"已设置代理: {proxy_address}")
            
            # 创建页面实例
            self.page = ChromiumPage(co)
            
            # 设置用户代理和加载模式
            self.page.set.user_agent(Config.USER_AGENT)
            self.page.set.load_mode.eager()
            
            logger.info("浏览器初始化完成")
            
        except Exception as e:
            raise Exception(f"初始化浏览器失败: {e}")
    
    def get(self, url: str):
        """导航到指定URL"""
        try:
            logger.info(f"访问页面: {url}")
            self.page.get(url)
            time.sleep(3)  # 等待页面加载
            
            current_url = self.page.url
            current_title = self.page.title
            
            logger.info(f"当前URL: {current_url}")
            logger.info(f"页面标题: {current_title}")
            
        except Exception as e:
            raise Exception(f"页面导航失败: {e}")
    
    @property
    def current_url(self) -> str:
        """获取当前URL"""
        return self.page.url if self.page else ""
    
    @property
    def title(self) -> str:
        """获取页面标题"""
        return self.page.title if self.page else ""
    
    @property
    def page_source(self) -> str:
        """获取页面源码"""
        return self.page.html if self.page else ""
    
    def find_elements_by_tag_name(self, tag_name: str):
        """查找元素（兼容Selenium接口）"""
        return self.page.eles(f"tag={tag_name}") if self.page else []
    
    def find_element_by_xpath(self, xpath: str):
        """通过XPath查找元素"""
        return self.page.ele(f"xpath:{xpath}") if self.page else None
    
    def find_element_by_css_selector(self, selector: str):
        """通过CSS选择器查找元素"""
        return self.page.ele(selector) if self.page else None
    
    def refresh(self):
        """刷新页面"""
        if self.page:
            self.page.refresh(ignore_cache=True)
            time.sleep(3)
    
    def quit(self):
        """关闭浏览器"""
        try:
            if self.page:
                self.page.quit()
                logger.info("浏览器已关闭")
        except:
            logger.warning("浏览器可能已经关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()