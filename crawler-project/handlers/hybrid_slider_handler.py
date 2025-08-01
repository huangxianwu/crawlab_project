#!/usr/bin/env python3
"""
混合滑块处理器
结合参考项目的成功算法 + Selenium实现
保持现有架构的同时采用参考项目的核心逻辑
"""
import time
import random
import requests
import cv2
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    import ddddocr
    DDDDOCR_AVAILABLE = True
except ImportError:
    DDDDOCR_AVAILABLE = False

class HybridSliderHandler:
    """
    混合滑块处理器
    采用参考项目的成功算法，适配到Selenium实现
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.det = None
        
        # 初始化ddddocr - 完全按照参考项目的方式
        if DDDDOCR_AVAILABLE:
            try:
                self.det = ddddocr.DdddOcr(det=False, ocr=False)
                print("✅ ddddocr滑块检测器初始化成功")
            except Exception as e:
                print(f"❌ ddddocr初始化失败: {e}")
                self.det = None
    
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
                    return False  # 无验证码
                
                if not has_captcha_container:
                    print("⚠️ 未找到captcha_container，但页面显示Security Check")
                    # 继续尝试处理
                
                if attempt == 0:
                    print("🔐 检测到验证码，正在处理...")
                else:
                    print(f"🔄 验证码处理重试 {attempt + 1}/3")
                
                # 查找验证码图片 - 适配参考项目的 page.eles("tag=img", timeout=20)
                imgs = self.find_captcha_images_reference_method()
                if len(imgs) < 2:
                    print("⚠️ 验证码图片不足")
                    continue
                
                try:
                    # 获取验证码图片URL - 完全按照参考项目的方式
                    background_img_url = imgs[0].get_attribute("src")
                    target_img_url = imgs[1].get_attribute("src")
                    
                    print(f"背景图URL: {background_img_url[:50]}...")
                    print(f"滑块图URL: {target_img_url[:50]}...")
                    
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
                                print(f"🎯 ddddocr识别到滑块位置: {target_x}")
                                
                                # 计算滑块位置的偏移量 - 参考项目的关键算法
                                actual_x = self.calculate_actual_distance_reference_algorithm(
                                    target_x, imgs[0], imgs[1], background_bytes
                                )
                                
                                print(f"📐 计算的实际滑动距离: {actual_x}")
                                
                                # 执行滑动操作 - 适配参考项目的 slider_element.drag(actual_x, 10, 0.2)
                                success = self.perform_drag_reference_method(actual_x)
                                if success:
                                    # 检查验证码是否通过 - 参考项目的验证方式
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
                            # 如果滑块识别失败，使用随机位移作为备选方案 - 参考项目的备选方案
                            slide_distance = random.randint(100, 200)
                            print(f"🎲 使用随机滑动距离: {slide_distance}")
                            success = self.perform_drag_reference_method(slide_distance)
                            if success:
                                time.sleep(3)
                    
                    # 等待一段时间再重试 - 参考项目的重试逻辑
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
    
    def find_captcha_images_reference_method(self):
        """
        查找验证码图片 - 适配参考项目的方法
        参考项目: imgs = page.eles("tag=img", timeout=20)
        """
        try:
            # 等待图片加载
            time.sleep(2)
            
            # 查找所有图片元素
            imgs = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"页面总共找到 {len(imgs)} 张图片")
            
            # 筛选验证码相关图片
            captcha_imgs = []
            for i, img in enumerate(imgs):
                try:
                    if img.is_displayed():
                        src = img.get_attribute('src') or ''
                        size = img.size
                        
                        # 检查图片尺寸和来源
                        if size['width'] > 50 and size['height'] > 50:
                            print(f"图片 {i+1}: src={src[:50]}..., size={size}")
                            captcha_imgs.append(img)
                            
                            # 如果找到2张图片就够了（背景图+滑块图）
                            if len(captcha_imgs) >= 2:
                                break
                except:
                    continue
            
            print(f"筛选出 {len(captcha_imgs)} 张验证码图片")
            return captcha_imgs
            
        except Exception as e:
            print(f"查找验证码图片失败: {e}")
            return []
    
    def calculate_actual_distance_reference_algorithm(self, target_x, bg_img, target_img, bg_bytes):
        """
        计算实际滑动距离 - 完全按照参考项目的算法
        参考项目的关键算法:
        x_offset = imgs[1].rect.location[0] - imgs[0].rect.location[0]
        actual_x = target_x * (340 / width) - x_offset
        """
        try:
            # 计算滑块位置的偏移量 - 参考项目的方法
            bg_location = bg_img.location
            target_location = target_img.location
            x_offset = target_location['x'] - bg_location['x']
            
            print(f"📐 背景图位置: {bg_location}")
            print(f"📐 滑块图位置: {target_location}")
            print(f"📐 位置偏移: {x_offset}")
            
            # 获取图片尺寸进行缩放 - 参考项目的精确算法
            img_array = np.frombuffer(bg_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is not None:
                height, width = img.shape[:2]
                # 按比例缩放到实际滑块位置 - 参考项目的关键算法
                actual_x = target_x * (340 / width) - x_offset
                
                print(f"📐 图片原始尺寸: {width}x{height}")
                print(f"📐 缩放比例: {340/width}")
                print(f"📐 计算公式: {target_x} * ({340}/{width}) - {x_offset} = {actual_x}")
            else:
                actual_x = target_x - x_offset
                print(f"📐 无法解析图片，使用简化计算: {target_x} - {x_offset} = {actual_x}")
            
            return actual_x
            
        except Exception as e:
            print(f"距离计算失败: {e}")
            return target_x
    
    def perform_drag_reference_method(self, distance):
        """
        执行拖拽操作 - 适配参考项目的 slider_element.drag(actual_x, 10, 0.2)
        参考项目: slider_element.drag(actual_x, 10, 0.2)
        """
        try:
            # 查找滑块元素 - 使用参考项目的精确选择器
            slider_element = None
            
            # 参考项目的选择器: "xpath://*[@id='secsdk-captcha-drag-wrapper']/div[2]"
            try:
                slider_element = self.driver.find_element(
                    By.XPATH, "//*[@id='secsdk-captcha-drag-wrapper']/div[2]"
                )
                if slider_element and slider_element.is_displayed():
                    print("✅ 找到滑块元素: secsdk-captcha-drag-wrapper/div[2]")
                else:
                    slider_element = None
            except:
                pass
            
            # 备用选择器
            if not slider_element:
                backup_selectors = [
                    ".secsdk-captcha-drag-icon",
                    "#secsdk-captcha-drag-wrapper .secsdk-captcha-drag-icon"
                ]
                
                for selector in backup_selectors:
                    try:
                        slider_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if slider_element and slider_element.is_displayed():
                            print(f"✅ 找到滑块元素: {selector}")
                            break
                    except:
                        continue
            
            if not slider_element:
                print("❌ 未找到滑块元素")
                return False
            
            # 模拟参考项目的 drag(actual_x, 10, 0.2) 操作
            # actual_x: 水平距离, 10: 垂直偏移, 0.2: 持续时间
            
            print(f"🎯 开始拖拽: 水平={distance}, 垂直=10, 持续时间=0.2秒")
            
            actions = ActionChains(self.driver)
            
            # 点击并按住滑块
            actions.click_and_hold(slider_element)
            
            # 模拟0.2秒的拖拽过程，分解为多个小步骤
            steps = 8  # 0.2秒分8步，每步0.025秒
            step_distance = distance / steps
            step_delay = 0.2 / steps
            
            for i in range(steps):
                # 第一步添加垂直偏移10，后续步骤添加随机小偏移
                y_offset = 10 if i == 0 else random.randint(-1, 1)
                actions.move_by_offset(step_distance, y_offset)
                time.sleep(step_delay)
                print(f"步骤 {i+1}/{steps}: 移动 ({step_distance:.1f}, {y_offset})")
            
            # 释放鼠标
            actions.release()
            actions.perform()
            
            print("✅ 拖拽操作执行完成")
            return True
            
        except Exception as e:
            print(f"❌ 拖拽操作失败: {e}")
            return False