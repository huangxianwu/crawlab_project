"""
滑块验证处理器
基于TikTok项目实战经验，使用ddddocr进行智能识别
参考: https://github.com/huangxianwu/tiktok_web_crawler_pyqt
"""
import time
import random
import requests
import cv2
import numpy as np
from typing import Optional, Tuple, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import Config
from utils.logger import get_logger

try:
    import ddddocr
    DDDDOCR_AVAILABLE = True
except ImportError:
    DDDDOCR_AVAILABLE = False

logger = get_logger(__name__)


class SliderHandler:
    """滑块验证处理器 - 基于TikTok项目经验"""
    
    def __init__(self, driver):
        """
        初始化滑块处理器
        
        Args:
            driver: Selenium WebDriver实例
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.ELEMENT_WAIT_TIMEOUT)
        
        # 初始化ddddocr滑块检测器
        self.det = None
        if DDDDOCR_AVAILABLE:
            try:
                self.det = ddddocr.DdddOcr(det=False, ocr=False)
                logger.info("ddddocr滑块检测器初始化成功")
            except Exception as e:
                logger.error(f"ddddocr初始化失败: {e}")
                self.det = None
        else:
            logger.warning("ddddocr未安装，将使用备用滑块处理方案")
    
    def detect_slider(self) -> bool:
        """
        检测是否存在滑块验证
        使用多重检测策略确保准确性
        
        Returns:
            bool: 是否检测到滑块验证
        """
        try:
            # 方法1: 检查HTML中的验证码容器
            page_source = self.driver.page_source
            captcha_keywords = [
                'captcha_container',
                'secsdk-captcha',
                'captcha-verify',
                'slider-verify',
                'drag-verify'
            ]
            
            for keyword in captcha_keywords:
                if keyword in page_source:
                    logger.info(f"通过页面源码检测到滑块验证: {keyword}")
                    return True
            
            # 方法2: 检查验证码容器元素
            captcha_selectors = [
                Config.CAPTCHA_CONTAINER_SELECTOR,
                ".captcha-container",
                ".slider-container",
                ".slide-verify",
                "[class*='captcha']",
                "[id*='captcha']",
                ".secsdk-captcha-drag-wrapper"
            ]
            
            for selector in captcha_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        logger.info(f"检测到滑块容器: {selector}")
                        return True
                except (NoSuchElementException, TimeoutException):
                    continue
            
            # 方法3: 检查验证码图片元素
            try:
                imgs = self.driver.find_elements(By.TAG_NAME, "img")
                captcha_imgs = []
                
                for img in imgs:
                    src = img.get_attribute('src') or ''
                    alt = img.get_attribute('alt') or ''
                    class_name = img.get_attribute('class') or ''
                    
                    if any(keyword in (src + alt + class_name).lower() 
                          for keyword in ['captcha', 'verify', 'slider', 'drag']):
                        captcha_imgs.append(img)
                
                if len(captcha_imgs) >= 2:  # 通常需要背景图和滑块图
                    logger.info(f"检测到滑块验证图片: {len(captcha_imgs)}张")
                    return True
                    
            except Exception as e:
                logger.debug(f"检查验证码图片时出错: {e}")
            
            # 方法4: 检查滑块拖拽元素
            slider_selectors = [
                Config.SLIDER_BUTTON_SELECTOR,
                ".secsdk-captcha-drag-icon",
                ".slider-button",
                ".drag-button",
                "[class*='drag-icon']"
            ]
            
            for selector in slider_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        logger.info(f"检测到滑块拖拽元素: {selector}")
                        return True
                except (NoSuchElementException, TimeoutException):
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"滑块检测失败: {e}")
            return False
    
    def solve_slider_captcha(self) -> bool:
        """
        解决滑块验证码
        基于ddddocr图像识别的智能滑块处理
        
        Returns:
            bool: 滑块处理是否成功
        """
        if not self.det:
            logger.warning("ddddocr未初始化，使用备用方案")
            return self.fallback_random_slide()
        
        try:
            # 查找滑块相关元素
            slider_images = self.find_slider_images()
            if len(slider_images) < 2:
                logger.warning("滑块图片不足，使用备用方案")
                return self.fallback_random_slide()
            
            # 获取背景图和滑块图
            background_img = slider_images[0]
            target_img = slider_images[1]
            
            background_url = background_img.get_attribute("src")
            target_url = target_img.get_attribute("src")
            
            if not background_url or not target_url:
                logger.warning("无法获取滑块图片URL")
                return self.fallback_random_slide()
            
            # 下载图片
            background_response = requests.get(background_url, timeout=10)
            target_response = requests.get(target_url, timeout=10)
            
            if background_response.status_code != 200 or target_response.status_code != 200:
                logger.warning("滑块图片下载失败")
                return self.fallback_random_slide()
            
            # 使用ddddocr识别滑块位置
            background_bytes = background_response.content
            target_bytes = target_response.content
            
            res = self.det.slide_match(target_bytes, background_bytes)
            if not res or "target" not in res:
                logger.warning("ddddocr识别失败，使用备用方案")
                return self.fallback_random_slide()
            
            target_x = res["target"][0]
            logger.info(f"ddddocr识别到滑块位置: {target_x}")
            
            # 计算实际滑动距离
            actual_distance = self.calculate_actual_distance(
                target_x, background_img, target_img, background_bytes
            )
            
            # 执行滑动操作
            return self.perform_slide(actual_distance)
            
        except Exception as e:
            logger.error(f"滑块识别处理失败: {e}")
            return self.fallback_random_slide()
    
    def find_slider_images(self) -> List:
        """
        查找滑块相关图片
        
        Returns:
            List: 滑块图片元素列表
        """
        slider_images = []
        
        try:
            # 查找所有图片元素
            imgs = self.driver.find_elements(By.TAG_NAME, "img")
            
            # 筛选滑块相关图片
            for img in imgs:
                src = img.get_attribute('src') or ''
                alt = img.get_attribute('alt') or ''
                class_name = img.get_attribute('class') or ''
                
                # 检查是否为滑块相关图片
                if any(keyword in (src + alt + class_name).lower() 
                      for keyword in ['captcha', 'verify', 'slider', 'bg', 'puzzle']):
                    if img.is_displayed() and img.size['width'] > 50:  # 过滤太小的图片
                        slider_images.append(img)
            
            # 按图片大小排序，通常背景图更大
            slider_images.sort(key=lambda x: x.size['width'] * x.size['height'], reverse=True)
            
            logger.debug(f"找到滑块图片: {len(slider_images)}张")
            return slider_images
            
        except Exception as e:
            logger.error(f"查找滑块图片失败: {e}")
            return []
    
    def calculate_actual_distance(self, target_x: int, bg_img, target_img, bg_bytes: bytes) -> float:
        """
        计算实际滑动距离
        考虑图片缩放比例和位置偏移
        
        Args:
            target_x: ddddocr识别的目标X坐标
            bg_img: 背景图片元素
            target_img: 滑块图片元素
            bg_bytes: 背景图片字节数据
            
        Returns:
            float: 实际滑动距离
        """
        try:
            # 获取图片在页面中的位置
            bg_location = bg_img.location
            target_location = target_img.location
            x_offset = target_location['x'] - bg_location['x']
            
            # 获取图片实际尺寸
            img_array = np.frombuffer(bg_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is not None:
                height, width = img.shape[:2]
                # 获取页面中图片的显示尺寸
                bg_size = bg_img.size
                scale_ratio = bg_size['width'] / width if width > 0 else 1
                actual_distance = target_x * scale_ratio - x_offset
            else:
                actual_distance = target_x - x_offset
            
            # 确保距离为正数且在合理范围内
            actual_distance = max(0, min(actual_distance, 400))
            
            logger.info(f"计算实际滑动距离: {actual_distance}")
            return actual_distance
            
        except Exception as e:
            logger.error(f"距离计算失败: {e}")
            return target_x
    
    def perform_slide(self, distance: float) -> bool:
        """
        执行滑动操作
        使用人工轨迹模拟真实滑动
        
        Args:
            distance: 滑动距离
            
        Returns:
            bool: 滑动是否成功
        """
        try:
            # 查找滑块元素
            slider_element = self.find_slider_element()
            if not slider_element:
                logger.error("未找到滑块元素")
                return False
            
            # 生成人工滑动轨迹
            trajectory = self.generate_human_trajectory(distance)
            
            # 执行滑动操作
            actions = ActionChains(self.driver)
            actions.click_and_hold(slider_element)
            
            # 按轨迹移动
            for step in trajectory:
                actions.move_by_offset(step, random.randint(-2, 2))  # 添加垂直随机偏移
                time.sleep(random.uniform(0.01, 0.03))
            
            # 释放鼠标
            actions.release()
            actions.perform()
            
            logger.info("滑动操作执行完成")
            time.sleep(2)  # 等待验证结果
            
            # 验证是否成功
            success = not self.detect_slider()
            if success:
                logger.info("滑块验证成功")
            else:
                logger.warning("滑块验证可能失败")
            
            return success
            
        except Exception as e:
            logger.error(f"滑动操作失败: {e}")
            return False
    
    def find_slider_element(self):
        """
        查找滑块拖拽元素
        
        Returns:
            WebElement: 滑块元素，如果未找到返回None
        """
        slider_selectors = [
            Config.SLIDER_BUTTON_SELECTOR,
            ".secsdk-captcha-drag-icon",
            ".slider-button",
            ".slide-btn",
            ".drag-button",
            "[class*='slider']",
            "[class*='drag']",
            ".captcha-slider-btn"
        ]
        
        for selector in slider_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed() and element.is_enabled():
                    logger.debug(f"找到滑块元素: {selector}")
                    return element
            except (NoSuchElementException, TimeoutException):
                continue
        
        logger.error("未找到可用的滑块元素")
        return None
    
    def generate_human_trajectory(self, distance: float) -> List[int]:
        """
        生成模拟人工的滑动轨迹
        使用加速-减速模式模拟真实人工操作
        
        Args:
            distance: 总滑动距离
            
        Returns:
            List[int]: 滑动轨迹步长列表
        """
        trajectory = []
        current = 0
        mid = distance * 0.8  # 80%处开始减速
        
        while current < distance:
            if current < mid:
                # 加速阶段：随机加速度
                a = random.uniform(1, 3)
            else:
                # 减速阶段：随机减速度
                a = random.uniform(-3, -1)
            
            # 计算移动步长
            v0 = random.uniform(0, 1)
            move = v0 + 0.5 * a
            current += move
            
            # 确保不超过目标距离
            if current > distance:
                move = distance - (current - move)
            
            if move > 0:
                trajectory.append(round(move))
        
        logger.debug(f"生成滑动轨迹: 总距离={distance}, 步数={len(trajectory)}")
        return trajectory
    
    def fallback_random_slide(self) -> bool:
        """
        备用方案：随机滑动
        当ddddocr识别失败时使用
        
        Returns:
            bool: 滑动是否成功
        """
        try:
            logger.info("使用随机滑动备用方案")
            
            # 随机生成滑动距离
            distance = random.randint(100, 250)
            
            # 执行滑动
            return self.perform_slide(distance)
            
        except Exception as e:
            logger.error(f"随机滑动失败: {e}")
            return False
    
    def handle_captcha_with_retry(self, max_retries: int = 3) -> bool:
        """
        带重试机制的滑块处理
        
        Args:
            max_retries: 最大重试次数
            
        Returns:
            bool: 是否成功处理滑块（True表示无滑块或处理成功，False表示有滑块但处理失败）
        """
        for attempt in range(max_retries):
            try:
                # 检测滑块
                if not self.detect_slider():
                    logger.info("未检测到滑块验证")
                    return True  # 无滑块，返回成功
                
                logger.info(f"检测到滑块验证，开始处理 (尝试 {attempt + 1}/{max_retries})")
                
                # 尝试解决滑块
                if self.solve_slider_captcha():
                    logger.info("滑块验证处理成功")
                    return True
                
                # 失败后等待并重试
                if attempt < max_retries - 1:
                    wait_time = random.uniform(3, 6)
                    logger.warning(f"滑块处理失败，等待 {wait_time:.1f}s 后重试")
                    time.sleep(wait_time)
                    
                    # 刷新页面重试
                    try:
                        self.driver.refresh()
                        time.sleep(3)
                    except Exception as e:
                        logger.warning(f"页面刷新失败: {e}")
                
            except Exception as e:
                logger.error(f"滑块处理异常: {e}")
                continue
        
        logger.error(f"滑块处理失败，已尝试 {max_retries} 次")
        return False  # 处理失败
    
    def get_captcha_status(self) -> dict:
        """
        获取验证码状态信息
        
        Returns:
            dict: 验证码状态信息
        """
        status = {
            'has_captcha': False,
            'captcha_type': None,
            'images_found': 0,
            'slider_found': False,
            'ddddocr_available': DDDDOCR_AVAILABLE
        }
        
        try:
            status['has_captcha'] = self.detect_slider()
            
            if status['has_captcha']:
                # 检查验证码类型
                if self.find_slider_element():
                    status['captcha_type'] = 'slider'
                    status['slider_found'] = True
                
                # 统计图片数量
                slider_images = self.find_slider_images()
                status['images_found'] = len(slider_images)
        
        except Exception as e:
            logger.error(f"获取验证码状态失败: {e}")
        
        return status