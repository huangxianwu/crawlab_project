"""
滑块验证处理器
基于成功的TikTok项目实战经验，使用ddddocr进行智能识别
参考: https://github.com/huangxianwu/tiktok_web_crawler_pyqt
核心技术: 参考项目算法 + Selenium实现 + 精确位置计算
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
        使用参考项目的成功算法进行精确处理
        
        Returns:
            bool: 滑块处理是否成功
        """
        return self.handle_captcha_reference_algorithm()
    
    def handle_captcha_reference_algorithm(self) -> bool:
        """
        使用参考项目的完整算法处理滑块验证
        直接移植参考项目的 handle_captcha 方法逻辑
        """
        try:
            # 多次检查验证码，增加成功率 - 参考项目的重试机制
            for attempt in range(3):
                html_text = self.driver.page_source
                
                # 检查是否有验证码 - 参考项目的检测方法
                has_captcha_container = '<div id="captcha_container">' in html_text
                has_security_check = "Security Check" in self.driver.title
                
                if not has_captcha_container and not has_security_check:
                    return True  # 无验证码，返回成功
                
                if not has_captcha_container:
                    logger.warning("未找到captcha_container，但页面显示Security Check")
                    # 继续尝试处理
                
                if attempt == 0:
                    logger.info("检测到验证码，正在处理...")
                else:
                    logger.info(f"验证码处理重试 {attempt + 1}/3")
                
                # 查找验证码图片 - 适配参考项目的方法
                imgs = self.find_captcha_images_reference_method()
                if len(imgs) < 2:
                    logger.warning("验证码图片不足")
                    continue
                
                try:
                    # 获取验证码图片URL - 完全按照参考项目的方式
                    background_img_url = imgs[0].get_attribute("src")
                    target_img_url = imgs[1].get_attribute("src")
                    
                    logger.info(f"背景图URL: {background_img_url[:50]}...")
                    logger.info(f"滑块图URL: {target_img_url[:50]}...")
                    
                    # 下载验证码图片 - 参考项目的下载方式
                    background_response = requests.get(background_img_url, timeout=10)
                    target_response = requests.get(target_img_url, timeout=10)
                    
                    if background_response.status_code == 200 and target_response.status_code == 200:
                        # 使用ddddocr的滑块匹配功能 - 参考项目的核心算法
                        background_bytes = background_response.content
                        target_bytes = target_response.content
                        
                        # 使用滑块检测器识别位置 - 参考项目的识别逻辑
                        try:
                            res = self.det.slide_match(target_bytes, background_bytes)
                            if res and "target" in res:
                                target_x = res["target"][0]
                                logger.info(f"ddddocr识别到滑块位置: {target_x}")
                                
                                # 计算滑块位置的偏移量 - 参考项目的关键算法
                                actual_x = self.calculate_actual_distance_reference_algorithm(
                                    target_x, imgs[0], imgs[1], background_bytes
                                )
                                
                                logger.info(f"计算的实际滑动距离: {actual_x}")
                                
                                # 执行滑动操作 - 适配参考项目的方法
                                success = self.perform_drag_reference_method(actual_x)
                                if success:
                                    # 检查验证码是否通过 - 参考项目的验证方式
                                    time.sleep(3)
                                    new_html = self.driver.page_source
                                    if "captcha-verify-image" not in new_html:
                                        logger.info("验证码处理成功")
                                        return True  # 返回True表示处理成功
                                    else:
                                        logger.warning("验证码未通过，准备重试")
                                else:
                                    logger.error("滑动操作失败")
                            else:
                                logger.warning("滑块位置识别失败")
                                
                        except Exception as e:
                            logger.warning(f"滑块识别异常: {e}")
                            # 如果滑块识别失败，使用随机位移作为备选方案
                            slide_distance = random.randint(100, 200)
                            logger.info(f"使用随机滑动距离: {slide_distance}")
                            success = self.perform_drag_reference_method(slide_distance)
                            if success:
                                time.sleep(3)
                    
                    # 等待一段时间再重试 - 参考项目的重试逻辑
                    if attempt < 2:
                        time.sleep(2)
                        self.driver.refresh()
                        time.sleep(2)
                        
                except Exception as e:
                    logger.warning(f"验证码处理异常: {e}")
                    continue
            
            # 所有尝试都失败了
            logger.error("验证码处理失败，已尝试3次")
            return False  # 返回False表示处理失败
            
        except Exception as e:
            logger.error(f"滑块处理异常: {e}")
            return False
    
    def find_slider_images(self) -> List:
        """
        查找滑块相关图片
        专门针对TikTok的验证码图片结构
        
        Returns:
            List: 滑块图片元素列表
        """
        slider_images = []
        
        try:
            # 方法1: 查找验证码容器内的图片
            try:
                captcha_container = self.driver.find_element(By.CSS_SELECTOR, "#captcha_container")
                container_imgs = captcha_container.find_elements(By.TAG_NAME, "img")
                if container_imgs:
                    logger.info(f"在验证码容器中找到 {len(container_imgs)} 张图片")
                    slider_images.extend(container_imgs)
            except:
                pass
            
            # 方法2: 查找所有图片并筛选
            if not slider_images:
                imgs = self.driver.find_elements(By.TAG_NAME, "img")
                logger.info(f"页面总共找到 {len(imgs)} 张图片")
                
                for img in imgs:
                    try:
                        src = img.get_attribute('src') or ''
                        alt = img.get_attribute('alt') or ''
                        class_name = img.get_attribute('class') or ''
                        
                        # TikTok验证码图片特征
                        captcha_indicators = [
                            'captcha' in src.lower(),
                            'verify' in src.lower(), 
                            'slider' in src.lower(),
                            'puzzle' in src.lower(),
                            'bg' in src.lower() and 'captcha' in self.driver.page_source.lower(),
                            'secsdk' in (src + class_name).lower()
                        ]
                        
                        if any(captcha_indicators):
                            if img.is_displayed() and img.size['width'] > 30:
                                slider_images.append(img)
                                logger.info(f"找到验证码图片: src={src[:50]}..., size={img.size}")
                    except Exception as e:
                        logger.debug(f"检查图片时出错: {e}")
                        continue
            
            # 方法3: 如果还是没找到，尝试查找所有可见的较大图片
            if not slider_images:
                imgs = self.driver.find_elements(By.TAG_NAME, "img")
                for img in imgs:
                    try:
                        if img.is_displayed() and img.size['width'] > 100 and img.size['height'] > 50:
                            slider_images.append(img)
                    except:
                        continue
                
                if slider_images:
                    logger.info(f"使用备用方法找到 {len(slider_images)} 张可能的验证码图片")
            
            # 按图片大小排序，通常背景图更大
            slider_images.sort(key=lambda x: x.size['width'] * x.size['height'], reverse=True)
            
            logger.info(f"最终找到滑块图片: {len(slider_images)}张")
            return slider_images
            
        except Exception as e:
            logger.error(f"查找滑块图片失败: {e}")
            return []
    
    def calculate_precise_distance(self, target_x: int, bg_img, target_img, bg_bytes: bytes) -> float:
        """
        计算精确滑动距离
        基于成功项目的核心算法，考虑图片缩放比例和位置偏移
        
        Args:
            target_x: ddddocr识别的目标X坐标
            bg_img: 背景图片元素
            target_img: 滑块图片元素
            bg_bytes: 背景图片字节数据
            
        Returns:
            float: 实际滑动距离
        """
        try:
            # 获取图片位置偏移 - 成功项目的方法
            try:
                bg_rect = bg_img.rect if hasattr(bg_img, 'rect') else {'location': bg_img.location}
                target_rect = target_img.rect if hasattr(target_img, 'rect') else {'location': target_img.location}
                
                bg_location = bg_rect.get('location', bg_img.location)
                target_location = target_rect.get('location', target_img.location)
                
                x_offset = target_location[0] - bg_location[0]
            except:
                # 备用方法
                x_offset = target_img.location['x'] - bg_img.location['x']
            
            # 获取图片实际尺寸和缩放比例 - 成功项目的精确算法
            img_array = np.frombuffer(bg_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is not None:
                height, width = img.shape[:2]
                logger.info(f"图片原始尺寸: {width}x{height}")
                
                # 获取页面中图片的显示尺寸
                bg_size = bg_img.size
                logger.info(f"页面显示尺寸: {bg_size}")
                
                # 按比例缩放到实际滑块位置 - 成功项目使用340作为标准宽度
                scale_ratio = 340 / width if width > 0 else 1
                actual_distance = target_x * scale_ratio - x_offset
                
                logger.info(f"缩放比例: {scale_ratio}")
                logger.info(f"位置偏移: {x_offset}")
            else:
                # 如果无法解析图片，使用原始坐标减去偏移
                actual_distance = target_x - x_offset
                logger.warning("无法解析图片，使用简化计算")
            
            # 确保距离在合理范围内
            actual_distance = max(10, min(actual_distance, 350))
            
            logger.info(f"计算的精确滑动距离: {actual_distance}")
            return actual_distance
            
        except Exception as e:
            logger.error(f"精确距离计算失败: {e}")
            # 返回一个基于识别位置的合理估算
            return max(50, min(target_x * 0.6, 250))
    
    def perform_precise_slide(self, distance: float) -> bool:
        """
        执行精确滑动操作
        基于成功项目的滑动算法，使用TikTok特定的滑块元素
        
        Args:
            distance: 滑动距离
            
        Returns:
            bool: 滑动是否成功
        """
        try:
            # 使用成功项目的精确滑块选择器
            slider_element = None
            slider_xpath = "xpath://*[@id='secsdk-captcha-drag-wrapper']/div[2]"
            
            try:
                # 尝试使用XPath查找滑块元素
                slider_element = self.driver.find_element(By.XPATH, "//*[@id='secsdk-captcha-drag-wrapper']/div[2]")
                if slider_element and slider_element.is_displayed():
                    logger.info("找到滑块元素: secsdk-captcha-drag-wrapper")
                else:
                    slider_element = None
            except:
                pass
            
            # 备用选择器
            if not slider_element:
                slider_element = self.find_slider_element()
                
            if not slider_element:
                logger.error("未找到滑块元素")
                return False
            
            logger.info(f"开始执行精确滑动: {distance} 像素")
            
            # 使用成功项目的滑动方法 - 直接拖拽指定距离
            actions = ActionChains(self.driver)
            actions.click_and_hold(slider_element)
            
            # 添加初始延迟
            time.sleep(random.uniform(0.1, 0.2))
            
            # 执行滑动 - 成功项目使用简单的直接拖拽
            actions.move_by_offset(distance, random.randint(-2, 2))
            
            # 等待一小段时间模拟人工操作
            time.sleep(0.2)
            
            # 释放鼠标
            actions.release()
            actions.perform()
            
            logger.info("精确滑动操作执行完成")
            
            # 等待验证结果 - 成功项目等待3秒
            time.sleep(3)
            
            # 验证是否成功
            try:
                current_url = self.driver.current_url
                current_title = self.driver.title
                
                # 检查页面是否跳转或验证码消失
                if "Security Check" not in current_title:
                    logger.info("滑块验证成功 - 页面已跳转")
                    return True
                
                # 检查验证码是否还存在
                html_text = self.driver.page_source
                if "captcha-verify-image" not in html_text and "captcha_container" not in html_text:
                    logger.info("滑块验证成功 - 验证码已消失")
                    return True
                
                logger.warning("滑块验证可能失败 - 验证码仍然存在")
                return False
                
            except Exception as e:
                logger.warning(f"验证结果检查失败，可能是页面跳转: {e}")
                return True  # 假设验证成功
            
        except Exception as e:
            logger.error(f"精确滑动操作失败: {e}")
            return False
    
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
            logger.info(f"生成滑动轨迹: {len(trajectory)} 步，总距离: {sum(trajectory)}")
            
            # 执行滑动操作
            actions = ActionChains(self.driver)
            actions.click_and_hold(slider_element)
            
            # 添加初始延迟
            time.sleep(random.uniform(0.1, 0.3))
            
            # 按轨迹移动
            for i, step in enumerate(trajectory):
                try:
                    y_offset = random.randint(-2, 2)  # 添加垂直随机偏移
                    actions.move_by_offset(step, y_offset)
                    
                    # 随机延迟，模拟人工操作
                    delay = random.uniform(0.01, 0.05)
                    time.sleep(delay)
                    
                    # 每10步检查一次浏览器状态
                    if i % 10 == 0:
                        try:
                            # 检查浏览器是否还活着
                            self.driver.current_url
                        except:
                            logger.warning("浏览器连接中断，可能验证成功")
                            return True
                            
                except Exception as e:
                    logger.warning(f"滑动步骤 {i} 失败: {e}")
                    continue
            
            # 释放前稍作停顿
            time.sleep(random.uniform(0.1, 0.2))
            actions.release()
            actions.perform()
            
            logger.info("滑动操作执行完成")
            
            # 等待验证结果
            time.sleep(3)
            
            # 验证是否成功 - 需要处理可能的页面跳转
            try:
                current_url = self.driver.current_url
                current_title = self.driver.title
                
                # 如果URL变化或标题不再是Security Check，说明验证成功
                if "Security Check" not in current_title:
                    logger.info("滑块验证成功 - 页面已跳转")
                    return True
                
                # 否则检查滑块是否还存在
                success = not self.detect_slider()
                if success:
                    logger.info("滑块验证成功 - 滑块已消失")
                else:
                    logger.warning("滑块验证可能失败 - 滑块仍然存在")
                
                return success
                
            except Exception as e:
                logger.warning(f"验证结果检查失败，可能是页面跳转: {e}")
                return True  # 假设验证成功
            
        except Exception as e:
            logger.error(f"滑动操作失败: {e}")
            return False
    
    def find_slider_element(self):
        """
        查找滑块拖拽元素
        专门针对TikTok的滑块元素结构
        
        Returns:
            WebElement: 滑块元素，如果未找到返回None
        """
        # TikTok特定的滑块选择器
        slider_selectors = [
            "#secsdk-captcha-drag-wrapper .secsdk-captcha-drag-icon",
            ".secsdk-captcha-drag-icon", 
            "#captcha_container .secsdk-captcha-drag-icon",
            Config.SLIDER_BUTTON_SELECTOR,
            ".slider-button",
            ".slide-btn", 
            ".drag-button",
            "[class*='drag-icon']",
            "[class*='slider']",
            "[class*='drag']",
            ".captcha-slider-btn"
        ]
        
        for selector in slider_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # 检查元素是否可交互
                        try:
                            size = element.size
                            if size['width'] > 0 and size['height'] > 0:
                                logger.info(f"找到滑块元素: {selector}, 大小: {size}")
                                return element
                        except:
                            continue
            except (NoSuchElementException, TimeoutException):
                continue
        
        # 备用方法：查找所有可能的拖拽元素
        try:
            all_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'drag') or contains(@class, 'slider')]")
            for element in all_elements:
                if element.is_displayed() and element.is_enabled():
                    size = element.size
                    if size['width'] > 10 and size['height'] > 10:
                        logger.info(f"备用方法找到滑块元素: {element.tag_name}, class={element.get_attribute('class')}")
                        return element
        except:
            pass
        
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
        if distance <= 0:
            return [0]
        
        trajectory = []
        current = 0
        mid = distance * 0.8  # 80%处开始减速
        
        # 防止无限循环，设置最大步数
        max_steps = 50
        step_count = 0
        
        while current < distance and step_count < max_steps:
            step_count += 1
            
            if current < mid:
                # 加速阶段：随机加速度
                a = random.uniform(1, 3)
            else:
                # 减速阶段：随机减速度  
                a = random.uniform(-3, -1)
            
            # 计算移动步长
            v0 = random.uniform(0.5, 2)  # 增加最小速度
            move = v0 + 0.5 * a
            current += move
            
            # 确保不超过目标距离
            if current > distance:
                move = distance - (current - move)
            
            if move > 0:
                trajectory.append(max(1, round(move)))  # 确保每步至少移动1像素
        
        # 如果轨迹太短，补充一些步骤
        if len(trajectory) < 5:
            remaining = distance - sum(trajectory)
            if remaining > 0:
                steps_needed = 5 - len(trajectory)
                step_size = remaining / steps_needed
                for _ in range(steps_needed):
                    trajectory.append(max(1, round(step_size)))
        
        logger.info(f"生成滑动轨迹: 总距离={distance}, 步数={len(trajectory)}, 实际距离={sum(trajectory)}")
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
                        logger.warning(f"页面刷新失败，可能是页面跳转: {e}")
                        # 如果刷新失败，可能是验证成功后页面跳转了
                        return True
                
            except Exception as e:
                # 检查是否是因为页面跳转导致的异常
                if "no such window" in str(e) or "target window already closed" in str(e):
                    logger.info("检测到页面跳转，滑块验证可能成功")
                    return True
                else:
                    logger.error(f"滑块处理异常: {e}")
                    continue
        
        logger.error(f"滑块处理失败，已尝试 {max_retries} 次")
        return False  # 处理失败
    
    def get_proxies(self) -> Optional[dict]:
        """
        获取代理设置
        基于成功项目的代理配置
        
        Returns:
            dict: 代理配置字典，如果未配置则返回None
        """
        try:
            # 检查是否启用代理
            if hasattr(Config, 'PROXY_ENABLED') and Config.PROXY_ENABLED:
                proxy_host = getattr(Config, 'PROXY_HOST', '127.0.0.1')
                proxy_port = getattr(Config, 'PROXY_PORT', '10809')
                proxy_url = f"http://{proxy_host}:{proxy_port}"
                
                return {
                    'http': proxy_url,
                    'https': proxy_url
                }
            return None
        except Exception as e:
            logger.warning(f"获取代理配置失败: {e}")
            return None
    
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