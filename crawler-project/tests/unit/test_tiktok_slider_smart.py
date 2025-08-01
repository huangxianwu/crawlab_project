#!/usr/bin/env python3
"""
智能TikTok滑块处理测试
结合ddddocr图像识别获取精确滑动距离
"""
import os
import sys
import time
import random
import requests
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import ddddocr
    DDDDOCR_AVAILABLE = True
    print("✅ ddddocr可用")
except ImportError:
    DDDDOCR_AVAILABLE = False
    print("❌ ddddocr不可用")

def create_webdriver():
    """创建WebDriver"""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(30)
        
        return driver
    except Exception as e:
        print(f"WebDriver创建失败: {e}")
        return None

def find_captcha_images(driver):
    """查找验证码图片"""
    print("\n🔍 查找验证码图片...")
    
    captcha_images = []
    
    # 方法1: 在验证码容器中查找
    try:
        container = driver.find_element(By.CSS_SELECTOR, "#captcha_container")
        imgs = container.find_elements(By.TAG_NAME, "img")
        if imgs:
            print(f"在验证码容器中找到 {len(imgs)} 张图片")
            for i, img in enumerate(imgs):
                src = img.get_attribute('src')
                size = img.size
                print(f"图片 {i+1}: src={src[:50]}..., size={size}")
                if img.is_displayed() and size['width'] > 50:
                    captcha_images.append(img)
    except:
        print("未找到验证码容器")
    
    # 方法2: 查找所有图片并筛选
    if not captcha_images:
        print("尝试查找所有图片...")
        all_imgs = driver.find_elements(By.TAG_NAME, "img")
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

def get_precise_distance_with_ddddocr(driver):
    """使用ddddocr获取精确滑动距离"""
    if not DDDDOCR_AVAILABLE:
        print("ddddocr不可用，返回随机距离")
        return random.randint(120, 180)
    
    print("\n🎯 使用ddddocr分析滑块位置...")
    
    try:
        # 初始化ddddocr
        det = ddddocr.DdddOcr(det=False, ocr=False)
        
        # 查找验证码图片
        captcha_images = find_captcha_images(driver)
        
        if len(captcha_images) < 2:
            print("验证码图片不足，使用随机距离")
            return random.randint(120, 180)
        
        # 获取背景图和滑块图
        bg_img = captcha_images[0]  # 通常第一张是背景图
        target_img = captcha_images[1]  # 第二张是滑块图
        
        bg_url = bg_img.get_attribute('src')
        target_url = target_img.get_attribute('src')
        
        print(f"背景图URL: {bg_url[:50]}...")
        print(f"滑块图URL: {target_url[:50]}...")
        
        # 下载图片
        print("下载验证码图片...")
        bg_response = requests.get(bg_url, timeout=10)
        target_response = requests.get(target_url, timeout=10)
        
        if bg_response.status_code != 200 or target_response.status_code != 200:
            print("图片下载失败")
            return random.randint(120, 180)
        
        # 使用ddddocr识别
        print("使用ddddocr识别滑块位置...")
        bg_bytes = bg_response.content
        target_bytes = target_response.content
        
        result = det.slide_match(target_bytes, bg_bytes)
        
        if result and 'target' in result:
            target_x = result['target'][0]
            print(f"✅ ddddocr识别结果: x={target_x}")
            
            # 计算实际滑动距离
            # 获取图片实际尺寸
            img_array = np.frombuffer(bg_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is not None:
                height, width = img.shape[:2]
                bg_size = bg_img.size
                
                # 计算缩放比例
                scale_ratio = bg_size['width'] / width if width > 0 else 1
                actual_distance = target_x * scale_ratio
                
                print(f"图片原始尺寸: {width}x{height}")
                print(f"页面显示尺寸: {bg_size}")
                print(f"缩放比例: {scale_ratio}")
                print(f"计算的滑动距离: {actual_distance}")
                
                # 确保距离在合理范围内
                actual_distance = max(50, min(actual_distance, 300))
                return actual_distance
            else:
                print("无法解析图片，使用原始坐标")
                return max(50, min(target_x, 300))
        else:
            print("ddddocr识别失败")
            return random.randint(120, 180)
            
    except Exception as e:
        print(f"ddddocr处理失败: {e}")
        return random.randint(120, 180)

def perform_smart_slide(driver, distance):
    """执行智能滑动"""
    print(f"\n🎯 执行智能滑动 {distance:.1f} 像素...")
    
    # 查找滑块元素
    slider_element = None
    slider_selectors = [
        ".secsdk-captcha-drag-icon",
        "#secsdk-captcha-drag-wrapper .secsdk-captcha-drag-icon"
    ]
    
    for selector in slider_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    size = element.size
                    if size['width'] > 0 and size['height'] > 0:
                        print(f"✅ 找到滑块元素: {selector}, 大小: {size}")
                        slider_element = element
                        break
            if slider_element:
                break
        except:
            continue
    
    if not slider_element:
        print("❌ 未找到滑块元素")
        return False
    
    try:
        # 生成更真实的滑动轨迹
        trajectory = generate_realistic_trajectory(distance)
        print(f"生成轨迹: {len(trajectory)} 步")
        
        # 执行滑动
        actions = ActionChains(driver)
        actions.click_and_hold(slider_element)
        
        # 添加初始延迟
        time.sleep(random.uniform(0.1, 0.3))
        
        for i, step in enumerate(trajectory):
            # 添加垂直随机偏移模拟人工操作
            y_offset = random.randint(-2, 2)
            actions.move_by_offset(step, y_offset)
            
            # 随机延迟
            delay = random.uniform(0.01, 0.05)
            time.sleep(delay)
            
            if i % 5 == 0:  # 每5步打印一次进度
                print(f"进度: {i+1}/{len(trajectory)}")
        
        # 释放前稍作停顿
        time.sleep(random.uniform(0.1, 0.2))
        actions.release()
        actions.perform()
        
        print("✅ 滑动操作完成")
        return True
        
    except Exception as e:
        print(f"❌ 滑动操作失败: {e}")
        return False

def generate_realistic_trajectory(distance):
    """生成更真实的滑动轨迹"""
    trajectory = []
    current = 0
    
    # 分为三个阶段：加速、匀速、减速
    accel_distance = distance * 0.3
    uniform_distance = distance * 0.4  
    decel_distance = distance * 0.3
    
    # 加速阶段
    while current < accel_distance:
        step = random.uniform(1, 4)
        if current + step > accel_distance:
            step = accel_distance - current
        trajectory.append(round(step))
        current += step
    
    # 匀速阶段
    uniform_start = current
    while current < uniform_start + uniform_distance:
        step = random.uniform(3, 6)
        if current + step > uniform_start + uniform_distance:
            step = uniform_start + uniform_distance - current
        trajectory.append(round(step))
        current += step
    
    # 减速阶段
    decel_start = current
    while current < distance:
        step = random.uniform(1, 3)
        if current + step > distance:
            step = distance - current
        trajectory.append(round(step))
        current += step
    
    return trajectory

def test_smart_slider():
    """智能滑块测试"""
    print("🧠 TikTok智能滑块测试")
    print("=" * 50)
    
    driver = create_webdriver()
    if not driver:
        return False
    
    try:
        # 访问TikTok Shop
        search_url = "https://www.tiktok.com/shop/s/phone%20case"
        print(f"🔄 访问页面: {search_url}")
        
        driver.get(search_url)
        time.sleep(5)
        
        print(f"✅ 当前URL: {driver.current_url}")
        print(f"✅ 页面标题: {driver.title}")
        
        # 检查是否有滑块
        if "Security Check" not in driver.title:
            print("⚠️  未检测到滑块验证页面")
            return True
        
        # 获取精确滑动距离
        precise_distance = get_precise_distance_with_ddddocr(driver)
        print(f"\n🎯 计算的滑动距离: {precise_distance:.1f} 像素")
        
        # 尝试多次滑动
        for attempt in range(3):
            print(f"\n--- 尝试 {attempt + 1}/3 ---")
            
            # 使用计算的距离，加上一些随机偏移
            distance = precise_distance + random.uniform(-10, 10)
            success = perform_smart_slide(driver, distance)
            
            if success:
                # 等待验证结果
                time.sleep(3)
                
                # 检查是否成功
                new_title = driver.title
                new_url = driver.current_url
                
                print(f"验证后标题: {new_title}")
                print(f"验证后URL: {new_url}")
                
                if "Security Check" not in new_title or new_url != search_url:
                    print("🎉 滑块验证成功！页面已跳转")
                    break
                else:
                    print("⚠️  滑块仍然存在，调整距离重试...")
                    # 调整距离
                    precise_distance += random.uniform(-20, 20)
            else:
                print("❌ 滑动失败")
            
            if attempt < 2:
                print("等待3秒后重试...")
                time.sleep(3)
        
        # 显示最终状态
        print(f"\n📋 最终状态:")
        print(f"URL: {driver.current_url}")
        print(f"标题: {driver.title}")
        
        # 保持浏览器打开观察
        print(f"\n🔍 浏览器将保持打开30秒供观察...")
        for i in range(30, 0, -1):
            print(f"\r剩余时间: {i}秒", end="", flush=True)
            time.sleep(1)
        
        print("\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    
    finally:
        driver.quit()
        print("✅ WebDriver已关闭")

def main():
    """主函数"""
    print("TikTok智能滑块测试工具")
    print("结合ddddocr图像识别获取精确滑动距离")
    
    success = test_smart_slider()
    
    if success:
        print("\n✅ 测试完成")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main()