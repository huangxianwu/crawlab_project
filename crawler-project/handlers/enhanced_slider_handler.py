#!/usr/bin/env python3
"""
基于参考项目成功算法的增强滑块处理器
实现TikTok滑块验证的精确处理
"""
import time
import random
import requests
import cv2
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

try:
    import ddddocr
    DDDDOCR_AVAILABLE = True
except ImportError:
    DDDDOCR_AVAILABLE = False

class EnhancedSliderHandler:
    """基于参考项目成功算法的增强滑块处理器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.det = None
        
        # 初始化ddddocr
        if DDDDOCR_AVAILABLE:
            try:
                self.det = ddddocr.DdddOcr(det=False, ocr=False)
                print("✅ ddddocr滑块检测器初始化成功")
            except Exception as e:
                print(f"❌ ddddocr初始化失败: {e}")
                self.det = None
    
    def find_captcha_images(self):
        """查找验证码图片 - 基于参考项目的方法"""
        captcha_images = []
        
        try:
            # 方法1: 在验证码容器中查找
            try:
                container = self.driver.find_element(By.CSS_SELECTOR, "#captcha_container")
                imgs = container.find_elements(By.TAG_NAME, "img")
                if imgs:
                    print(f"在验证码容器中找到 {len(imgs)} 张图片")
                    for i, img in enumerate(imgs):
                        src = img.get_attribute('src')
                        size = img.size
                        print(f"图片 {i+1}: src={src[:50]}..., size={size}")
                        if img.is_displayed() and size['width'] > 50:
                            captcha_images.append(img)
                    return captcha_images
            except:
                print("未找到验证码容器，尝试其他方法")
            
            # 方法2: 查找所有图片并筛选
            all_imgs = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"页面总共 {len(all_imgs)} 张图片")
            
            for i, img in enumerate(all_imgs):
                try:
                    src = img.get_attribute('src') or ''
                    size = img.size
                    
                    # 检查是否为验证码相关图片
                    if (img.is_displayed() and 
                        size['width'] > 100 and size['height'] > 50 and
                        ('captcha' in src.lower() or 'verify' in src.lower() or 
                         size['width'] > 200)):  # 大图片可能是背景图
                        
                        print(f"可能的验证码图片 {i+1}: src={src[:50]}..., size={size}")
                        captcha_images.append(img)
                except:
                    continue
            
            print(f"最终找到 {len(captcha_images)} 张验证码图片")
            return captcha_images
            
        except Exception as e:
            print(f"查找验证码图片失败: {e}")
            return []
    
    def detect_slider(self) -> bool:
        """检测滑块验证码"""
        try:
            html_text = self.driver.page_source
            
            # 检查验证码容器 - 使用参考项目的检测方法
            if '<div id="captcha_container">' in html_text:
                print("✅ 检测到验证码容器")
                return True
            
            # 检查页面标题
            if "Security Check" in self.driver.title:
                print("✅ 检测到安全检查页面")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 滑块检测失败: {e}")
            return False
    
    def handle_captcha_reference_algorithm(self) -> bool:
        """
        使用参考项目的成功算法处理滑块验证
        基于 real_tiktok_scraping_service.py 的 handle_captcha 方法
        """
        try:
            # 多次检查验证码，增加成功率
            for attempt in range(3):
                html_text = self.driver.page_source
                
                # 检查是否有验证码
                if '<div id="captcha_container">' not in html_text and "Security Check" not in self.driver.title:
                    return False
                
                if attempt == 0:
                    print("🔐 检测到验证码，正在处理...")
                else:
                    print(f"🔄 验证码处理重试 {attempt + 1}/3")
                
                # 查找验证码图片 - 使用更精确的方法
                imgs = self.find_captcha_images()
                if len(imgs) < 2:
                    print(f"⚠️ 验证码图片不足，找到 {len(imgs)} 张")
                    continue
                
                try:
                    # 获取验证码图片URL
                    background_img_url = imgs[0].get_attribute("src")
                    target_img_url = imgs[1].get_attribute("src")
                    
                    print(f"背景图URL: {background_img_url[:50]}...")
                    print(f"滑块图URL: {target_img_url[:50]}...")
                    
                    # 下载验证码图片
                    background_response = requests.get(background_img_url, timeout=10)
                    target_response = requests.get(target_img_url, timeout=10)
                    
                    if background_response.status_code == 200 and target_response.status_code == 200:
                        # 使用ddddocr的滑块匹配功能 - 参考项目的核心算法
                        background_bytes = background_response.content
                        target_bytes = target_response.content
                        
                        # 使用滑块检测器识别位置
                        try:
                            res = self.det.slide_match(target_bytes, background_bytes)
                            if res and "target" in res:
                                target_x = res["target"][0]
                                print(f"🎯 ddddocr识别到滑块位置: {target_x}")
                                
                                # 计算滑块位置的偏移量 - 参考项目的关键算法
                                x_offset = imgs[1].location['x'] - imgs[0].location['x']
                                
                                # 获取图片尺寸进行缩放 - 参考项目的精确算法
                                img_array = np.frombuffer(background_bytes, dtype=np.uint8)
                                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                                if img is not None:
                                    height, width = img.shape[:2]
                                    # 按比例缩放到实际滑块位置 - 关键算法
                                    actual_x = target_x * (340 / width) - x_offset
                                    print(f"📐 图片原始尺寸: {width}x{height}")
                                    print(f"📐 缩放比例: {340/width}")
                                    print(f"📐 位置偏移: {x_offset}")
                                    print(f"📐 计算的实际滑动距离: {actual_x}")
                                else:
                                    actual_x = target_x - x_offset
                                    print(f"📐 使用原始坐标: {actual_x}")
                                
                                # 执行滑动操作 - 使用参考项目的滑动方法
                                success = self.perform_slide_reference_method(actual_x)
                                if success:
                                    # 检查验证码是否通过
                                    time.sleep(3)
                                    new_html = self.driver.page_source
                                    if "captcha-verify-image" not in new_html:
                                        print("✅ 验证码处理成功")
                                        return False  # 返回False表示无验证码
                                    else:
                                        print("⚠️ 验证码未通过，准备重试")
                                else:
                                    print("❌ 滑动操作失败")
                            else:
                                print("⚠️ 滑块位置识别失败")
                                
                        except Exception as e:
                            print(f"⚠️ 滑块识别异常: {e}")
                            # 如果滑块识别失败，使用随机位移作为备选方案
                            slide_distance = random.randint(100, 200)
                            print(f"🎲 使用随机滑动距离: {slide_distance}")
                            success = self.perform_slide_reference_method(slide_distance)
                            if success:
                                time.sleep(3)
                    
                    # 等待一段时间再重试
                    if attempt < 2:
                        time.sleep(2)
                        self.driver.refresh()
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"⚠️ 验证码处理异常: {e}")
                    continue
            
            # 所有尝试都失败了
            print("❌ 验证码处理失败，已尝试3次")
            return True  # 返回True表示有验证码但处理失败
            
        except Exception as e:
            print(f"❌ 滑块处理异常: {e}")
            return True
    
    def perform_slide_reference_method(self, distance: float) -> bool:
        """
        使用参考项目的滑动方法
        基于Selenium的ActionChains，模拟参考项目的drag操作
        """
        try:
            # 查找滑块元素 - 使用参考项目的精确选择器
            slider_element = None
            
            # 参考项目使用的选择器路径
            slider_selectors = [
                "xpath://*[@id='secsdk-captcha-drag-wrapper']/div[2]",
                ".secsdk-captcha-drag-icon",
                "#secsdk-captcha-drag-wrapper .secsdk-captcha-drag-icon"
            ]
            
            for selector in slider_selectors:
                try:
                    if selector.startswith("xpath:"):
                        # 处理xpath选择器
                        xpath = selector.replace("xpath:", "")
                        slider_element = self.driver.find_element(By.XPATH, xpath)
                    else:
                        slider_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if slider_element and slider_element.is_displayed():
                        print(f"✅ 找到滑块元素: {selector}")
                        break
                except:
                    continue
            
            if not slider_element:
                print("❌ 未找到滑块元素")
                return False
            
            # 模拟参考项目的drag操作
            # 参考项目: slider_element.drag(actual_x, 10, 0.2)
            # 转换为Selenium的ActionChains操作
            
            actions = ActionChains(self.driver)
            
            # 点击并按住滑块
            actions.click_and_hold(slider_element)
            
            # 添加初始延迟，模拟人工操作
            time.sleep(random.uniform(0.1, 0.3))
            
            # 执行滑动 - 模拟参考项目的drag(actual_x, 10, 0.2)
            # 分解为多个小步骤，持续0.2秒
            steps = 10
            step_distance = distance / steps
            step_delay = 0.2 / steps
            
            print(f"🎯 开始滑动: 总距离={distance:.1f}, 分{steps}步执行")
            
            for i in range(steps):
                # 添加垂直偏移，模拟参考项目的y=10参数
                y_offset = 10 if i == 0 else random.randint(-2, 2)
                actions.move_by_offset(step_distance, y_offset)
                time.sleep(step_delay)
                print(f"步骤 {i+1}/{steps}: 移动 {step_distance:.1f} 像素")
            
            # 释放鼠标
            actions.release()
            actions.perform()
            
            print("✅ 滑动操作执行完成")
            return True
            
        except Exception as e:
            print(f"❌ 滑动操作失败: {e}")
            return False