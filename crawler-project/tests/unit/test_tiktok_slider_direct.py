#!/usr/bin/env python3
"""
直接测试TikTok滑块处理
专门针对TikTok的滑块验证结构进行测试
"""
import os
import sys
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

def detect_tiktok_slider(driver):
    """检测TikTok滑块验证"""
    print("\n🔍 检测TikTok滑块验证...")
    
    # 检查页面源码
    page_source = driver.page_source
    print(f"页面内容长度: {len(page_source)} 字符")
    
    # 检查关键词
    keywords = ['captcha', 'verify', 'secsdk', 'slider', 'drag']
    found_keywords = [kw for kw in keywords if kw in page_source.lower()]
    if found_keywords:
        print(f"✅ 页面源码中发现验证码相关关键词: {found_keywords}")
    
    # 检查验证码容器
    containers_found = []
    container_selectors = [
        "#captcha_container",
        ".secsdk-captcha-drag-wrapper", 
        "[class*='captcha']",
        "[id*='captcha']"
    ]
    
    for selector in container_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                containers_found.append(f"{selector} ({len(elements)}个)")
        except:
            pass
    
    if containers_found:
        for container in containers_found:
            print(f"找到元素: {container}")
    
    # 检查滑块图片
    imgs = driver.find_elements(By.TAG_NAME, "img")
    captcha_imgs = 0
    for img in imgs:
        try:
            src = img.get_attribute('src') or ''
            if any(kw in src.lower() for kw in ['captcha', 'verify', 'slider']):
                captcha_imgs += 1
        except:
            pass
    
    print(f"找到验证码图片: {captcha_imgs}个")
    
    # 检查滑块元素
    slider_selectors = [
        ".secsdk-captcha-drag-icon",
        "[class*='drag-icon']",
        "[class*='slider']"
    ]
    
    slider_found = False
    for selector in slider_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"找到滑块元素: {selector} ({len(elements)}个)")
                slider_found = True
        except:
            pass
    
    has_slider = len(found_keywords) > 0 or len(containers_found) > 0 or slider_found
    
    status = {
        'has_captcha': has_slider,
        'captcha_type': 'slider' if slider_found else 'unknown',
        'images_found': captcha_imgs,
        'slider_found': slider_found,
        'ddddocr_available': True
    }
    
    print(f"滑块检测结果: {'检测到滑块验证码' if has_slider else '未检测到滑块'}")
    print(f"状态: {status}")
    
    return has_slider

def perform_direct_slide(driver, distance=150):
    """直接执行滑动操作"""
    print(f"\n🔄 尝试直接滑动 {distance} 像素...")
    
    # 查找滑块元素
    slider_selectors = [
        ".secsdk-captcha-drag-icon",
        "#secsdk-captcha-drag-wrapper .secsdk-captcha-drag-icon",
        "[class*='drag-icon']",
        "[class*='slider']"
    ]
    
    slider_element = None
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
        except Exception as e:
            print(f"查找 {selector} 时出错: {e}")
            continue
    
    if not slider_element:
        print("❌ 未找到滑块元素")
        return False
    
    try:
        # 生成简单的滑动轨迹
        steps = []
        current = 0
        while current < distance:
            step = random.randint(3, 8)
            if current + step > distance:
                step = distance - current
            steps.append(step)
            current += step
        
        print(f"生成滑动轨迹: {len(steps)} 步, 总距离: {sum(steps)}")
        
        # 执行滑动
        actions = ActionChains(driver)
        actions.click_and_hold(slider_element)
        
        print("开始滑动...")
        for i, step in enumerate(steps):
            actions.move_by_offset(step, random.randint(-1, 1))
            time.sleep(random.uniform(0.02, 0.05))
            print(f"步骤 {i+1}/{len(steps)}: 移动 {step} 像素")
        
        actions.release()
        actions.perform()
        
        print("✅ 滑动操作完成")
        time.sleep(3)  # 等待验证结果
        
        return True
        
    except Exception as e:
        print(f"❌ 滑动操作失败: {e}")
        return False

def test_tiktok_slider():
    """测试TikTok滑块处理"""
    print("🎯 TikTok滑块直接测试")
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
        
        # 检测滑块
        has_slider = detect_tiktok_slider(driver)
        
        if has_slider:
            print("\n🎯 检测到滑块，开始处理...")
            
            # 尝试多次滑动
            for attempt in range(3):
                print(f"\n--- 尝试 {attempt + 1}/3 ---")
                
                # 随机距离滑动
                distance = random.randint(120, 200)
                success = perform_direct_slide(driver, distance)
                
                if success:
                    # 检查是否还有滑块
                    time.sleep(2)
                    if not detect_tiktok_slider(driver):
                        print("🎉 滑块验证成功！")
                        break
                    else:
                        print("⚠️  滑块仍然存在，继续尝试...")
                else:
                    print("❌ 滑动失败")
                
                if attempt < 2:
                    print("等待3秒后重试...")
                    time.sleep(3)
            
        else:
            print("⚠️  未检测到滑块验证")
        
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
    print("TikTok滑块直接测试工具")
    print("专门测试TikTok Shop的滑块验证处理")
    
    success = test_tiktok_slider()
    
    if success:
        print("\n✅ 测试完成")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main()